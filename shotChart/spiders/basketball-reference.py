import scrapy
import json
from datetime import date, timedelta
import datetime
# import boto3
from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
import logging

class BBSpider(scrapy.Spider):
    name = "basketball-reference" #identifies the spider, must be unique

    def start_requests(self):
        logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(funcName)s:%(levelname)s:%(message)s')
        logger = logging.getLogger("basketball-reference-scraper")
        logger.setLevel("INFO")
        #must return an iterable of Requests which the Spider will begin to crawl from.
        season = getattr(self, 'season', None)
        logger.info("Season is {}".format(season))
        topic = getattr(self, 'topic', None)
        logger.info("Topic is {}".format(topic))
        kafka_listener = getattr(self, 'kafka_listener', None)
        logger.info("Kafka listener is {}".format(kafka_listener))
        start_date = getattr(self, 'start_date', None)
        logger.info("Start date is {}".format(start_date))
        end_date = getattr(self, 'end_date', None)
        logger.info("End date is {}".format(end_date))
        #if you pass both season and (start_date and end_date), it will ignore the season argument. 

        urls = []
        with open('./calendar.json') as json_file:
            data = json.load(json_file)
            for p in data['seasons']:
                if str(p['year']) != str(season):
                    continue
                calendar_start_month = p['regular_start_month']
                calendar_start_day = p['regular_start_day']
                calendar_start_year = p['year']
                calendar_end_month = p['regular_end_month']
                calendar_end_day = p['regular_end_day']
                calendar_end_year = p['year'] + 1
                # if no start_date or end_date were passed, we read from calendar
                if not start_date:
                    start_date = date(calendar_start_year, calendar_start_month, calendar_start_day)
                else:
                    year = str(start_date).split('-')[0]
                    month = str(start_date).split('-')[1]
                    day = str(start_date).split('-')[2]
                    start_date = date(int(year), int(month), int(day))
                if not end_date:    
                    end_date = date(calendar_end_year, calendar_end_month, calendar_end_day)
                else:
                    year = str(end_date).split('-')[0]
                    month = str(end_date).split('-')[1]
                    day = str(end_date).split('-')[2]
                    end_date = date(int(year), int(month), int(day))
                delta = timedelta(days=1)
                while start_date <= end_date:
                    year = str(start_date).split('-')[0]
                    month = str(start_date).split('-')[1]
                    day = str(start_date).split('-')[2]
                    urls.append('https://www.basketball-reference.com/boxscores/?' + 'month=' + month + '&day=' + day +
                                '&year=' + year)
                    start_date += delta
        # create kafka topic always with the same name if it doesn't exist.
        # if kafka_listener:
        #     try:
        #         admin = KafkaAdminClient(bootstrap_servers=[kafka_listener])
        #         list_of_topics = admin.list_topics()
        #         logger.info("List of topics: {}".format(list_of_topics))
        #         my_topic = [topic for topic in list_of_topics if topic == "shot_charts"]
        #         logger.info("Does shot_charts exist?: {}".format(my_topic))
        #         if not my_topic:
        #             logger.info("Creating a new topic")
        #             topic = NewTopic(name='shot_charts',
        #                         num_partitions=1,
        #                         replication_factor=1)
        #             admin.create_topics([topic])
        #     except Exception as e:
        #         print(f"Error creating kafka topic. Error: {e}")
        #         return
        logger.info("Starting the scraper")
        for url in urls:
            logger.info("Sending request for URL: {}".format(url))
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
                logger = logging.getLogger("basketball-reference-scraper")
                logger.info("Loading {}".format(json.dumps(data)))

                # Kinesis
                # if stream:
                #     client = boto3.client('kinesis')
                #     client.put_record(StreamName="shot_charts", Data=json.dumps(data), PartitionKey="partitionkeydata")

                # Kafka Producer - local Kafka
                if topic and kafka_listener:
                    producer = KafkaProducer(
                        bootstrap_servers=[kafka_listener]
                    )
                    logger.info(f'Producing message @ {datetime.datetime.now()} | Message = {str(json.dumps(data))}')
                    producer.send(topic, json.dumps(data).encode("utf-8"))

                yield data
                

