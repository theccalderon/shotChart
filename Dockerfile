FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD scrapy crawl basketball-reference -a season=2019 -a topic=shot_charts -a kafka_listener='kafka:9092'