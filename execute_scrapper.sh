#!/usr/bin/env bash

start_season=2000
while [ $start_season -le 2019 ]
do
#    ../bin/scrapy crawl basketball-reference -o "shots-${start_season}.csv" -a season=${start_season}
#    touch  "shots-${start_season}.csv"
    scrapy crawl basketball-reference -o "shots-${start_season}.csv" -a season=${start_season}
    start_season=$((start_season + 1))
done

