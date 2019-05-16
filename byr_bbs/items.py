# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import scrapy


class BoardItem(scrapy.Item):
    board_name = scrapy.Field()
    board_url = scrapy.Field()
    parent_section = scrapy.Field()


class ArticleItem(scrapy.Item):
    title = scrapy.Field()
    poster = scrapy.Field()
    gid = scrapy.Field()
    url = scrapy.Field()
    reply_time = scrapy.Field()
    reply_count = scrapy.Field()
    articles = scrapy.Field()
