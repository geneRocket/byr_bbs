# -*- coding: utf-8 -*-
import json
import re

from elasticsearch import Elasticsearch


class LoadEs(object):
    def __init__(self):
        self.es = Elasticsearch(hosts="http://localhost:9200")
        self.tmp_set = set()
        if not self.es.indices.exists(index='byr_articles'):
            self.es.indices.create(index='byr_articles', ignore=400)

    def process_item(self):
        i = 0
        for line in open("byr_data.json", "r"):
            i += 1
            try:
                item = json.loads(line)
                results = re.findall('https://bbs.byr.cn/#!article/(.*?)/(\d+)', item['url'])
                item_id = results[0][0] + results[0][1]
                self.tmp_set.add(item['url'])
                self.es.index(index='byr_articles', id=item_id, body=item)
            except Exception as e:
                print(line)
                print(e)
            if i % 1000 == 0:
                print(len(self.tmp_set))


load = LoadEs()
load.process_item()
