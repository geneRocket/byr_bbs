# -*- coding: utf-8 -*-
import re

from elasticsearch import Elasticsearch


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ByrBbsPipeline(object):
    def __init__(self):
        self.es = Elasticsearch()
        self.id = 0
        self.tmp_set = set()
        if not self.es.indices.exists('bbs_articles_demo'):
            self.es.indices.create(index='bbs_articles_demo', ignore=400)

    def process_item(self, item, spider):
        print('=' * 80)
        print('id = ' + str(self.id), item['title'])
        print(item['url'])
        data_dict = dict(item)
        if item['url'] not in self.tmp_set:
            results = re.findall('https://bbs.byr.cn/#!article/(.*?)/(\d+)', item['url'])
            item_id = results[0][0] + results[0][1]
            self.tmp_set.add(item['url'])
            self.es.create(index='bbs_articles_demo', id=item_id, body=data_dict)
            self.id += 1
        else:
            print('>' * 37 + '已去重' + '<' * 37)

        return item
