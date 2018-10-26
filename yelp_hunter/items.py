# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class YelpHunterItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    phone = scrapy.Field()
    website = scrapy.Field()
    email = scrapy.Field()
