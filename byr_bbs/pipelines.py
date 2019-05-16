# -*- coding: utf-8 -*-
import json

from elasticsearch import Elasticsearch


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ByrBbsPipeline(object):
    def __init__(self):
        self.es = Elasticsearch()
        self.id = 1
        self.es.indices.create(index='bbs_articles', ignore=400)

    def process_item(self, item, spider):
        print(item['title'])
        print(item['url'])
        print('=' * 80)
        data_dict = dict(item)
        result = self.es.create(index='bbs_articles', id=self.id, body=data_dict)
        self.id += 1
        print('id =', result)

        return item
