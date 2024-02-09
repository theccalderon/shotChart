import scrapy
import json
from datetime import date, timedelta
import datetime
# import boto3
from kafka import KafkaProducer

class BBSpider(scrapy.Spider):
    name = "basketball-reference" #identifies the spider, must be unique

    #shortcut for start_requests
    # start_urls = [
    #     'https://www.basketball-reference.com/boxscores/?',
    # ]

    def start_requests(self):
        #must return an iterable of Requests which the Spider will begin to crawl from.
        
        season = getattr(self, 'season', None)
        topic = getattr(self, 'topic', None)
        kafka_listener = getattr(self, 'kafka_listener', None)

        urls = []
        with open('./calendar.json') as json_file:
            data = json.load(json_file)
            for p in data['seasons']:
                # print(p)
                if str(p['year']) != str(season):
                    continue
                start_month = p['regular_start_month']
                start_day = p['regular_start_day']
                start_year = p['year']
                end_month = p['regular_end_month']
                end_day = p['regular_end_day']
                end_year = p['year'] + 1
                start_date = date(start_year, start_month, start_day)
                end_date = date(end_year, end_month, end_day)
                delta = timedelta(days=1)
                while start_date <= end_date:
                    # print(start_date)
                    year = str(start_date).split('-')[0]
                    month = str(start_date).split('-')[1]
                    day = str(start_date).split('-')[2]
                    urls.append('https://www.basketball-reference.com/boxscores/?' + 'month=' + month + '&day=' + day +
                                '&year=' + year)
                    start_date += delta

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_games, cb_kwargs=dict(topic=topic,kafka_listener=kafka_listener))

    def parse_games(self, response, topic, kafka_listener):
        #will be called to handle the response downloaded for each of the requests made. The response parameter is an instance of TextResponse
        # that holds the page content and has further helpful methods to handle it.
        main_url = response.url
        # https://www.basketball-reference.com/boxscores/?month=10&day=31&year=2000
        year = str(main_url).split('?')[1].split('&')[2].split('=')[1]
        day = str(main_url).split('?')[1].split('&')[1].split('=')[1]
        month = str(main_url).split('?')[1].split('&')[0].split('=')[1]

        for game in response.css('div.game_summary.expanded.nohover'):
            next_page = game.css('p.links a::attr(href)')[2].get()
            # print(next_page)
            game_id = str(next_page).split('/')[3].split('.')[0]
            # print(game_id)
            winner = game.css('tr.winner td a::text').get()
            # print(winner)
            loser = game.css('tr.loser td a::text').get()
            # print(loser)
            # yield response.follow(next_page, callback=self.parse_shot_chart)
            request = scrapy.Request('https://www.basketball-reference.com/'+next_page,
                                     callback=self.parse_shot_chart,
                                     cb_kwargs=dict(game_id=game_id, winner=winner, loser=loser, year=year,
                                                    month=month, day=day, topic=topic, kafka_listener=kafka_listener))
            # request.cb_kwargs['foo'] = 'bar'  # add more arguments for the callback
            yield request

    def parse_shot_chart(self, response, game_id, winner, loser, year, month, day, topic, kafka_listener):
        for chart in response.css('div.shot-area'):
            # team = str(chart.css('::attr(id)').get()).split('-')[1]
            # print(team)
            for shot in chart.css('div.tooltip'):
                style = str(shot.css('::attr(style)').get()).split(';')
                x = style[0].split(':')[1]
                y = style[1].split(':')[1]
                # print(x)
                # print(y)
                shot_description = str(shot.css('::attr(tip)').get())
                # print(play)
                data = {
                    'game_id': game_id,
                    'year': year,
                    'month': month,
                    'day': day,
                    'winner': winner,
                    'loser': loser,
                    'x': x,
                    'y': y,
                    'play': shot_description,
                }
                print("loading ",json.dumps(data))

                # Kinesis
                # if stream:
                #     client = boto3.client('kinesis')
                #     client.put_record(StreamName="shot_charts", Data=json.dumps(data), PartitionKey="partitionkeydata")

                # Kafka Producer - local Kafka
                if topic and kafka_listener:
                    producer = KafkaProducer(
                        bootstrap_servers=[kafka_listener]
                    )
                    print(f'Producing message @ {datetime.datetime.now()} | Message = {str(json.dumps(data))}')
                    producer.send(topic, json.dumps(data).encode("utf-8"))

                yield data
                

