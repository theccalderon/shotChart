# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Season(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    year = scrapy.Field()
    regular_start_month = scrapy.Field()
    regular_start_day = scrapy.Field()
    regular_end_month = scrapy.Field()
    regular_end_day = scrapy.Field()
    playoffs_start_month = scrapy.Field()
    playoffs_start_day = scrapy.Field()
    playoffs_end_month = scrapy.Field()
    playoffs_end_day = scrapy.Field()
    games = []


class Game(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    game_id = scrapy.Field()
    winner = scrapy.Field()
    loser = scrapy.Field()
    shots = []

class ShotAttempt(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    x = scrapy.Field()
    y = scrapy.Field()
    desc = scrapy.Field()




