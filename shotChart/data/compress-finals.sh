#!/usr/bin/env bash

start_season=2019
while [ $start_season -le 2020 ]
do
    tar czvf "shots-${start_season}.tgz" "shots-${start_season}.csv"
#    touch  "shots-${start_season}.csv"
    start_season=$((start_season + 1))
done

