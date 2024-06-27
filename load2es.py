# -*- coding: utf-8 -*-
import json
import re

from elasticsearch import Elasticsearch


def get_mapping():
    return {
        "mappings": {
            "properties": {
                "articles": {
                    "properties": {
                        "article_contents": {
                            "type": "text",
                            "analyzer": "ik_smart",

                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        },
                        "id": {
                            "type": "keyword",

                        },
                        "pos": {
                            "type": "long"
                        },
                        "time": {
                            "type": "keyword",

                        },
                        "user_name": {
                            "type": "keyword",

                        },
                        "votedown_count": {
                            "type": "long",
                        },
                        "voteup_count": {
                            "type": "long",
                        }
                    }
                },
                "gid": {
                    "type": "long"
                },
                "poster": {
                    "type": "keyword",

                },
                "reply_count": {
                    "type": "long"
                },
                "reply_time": {
                    "type": "keyword",
                },
                "title": {
                    "type": "text",
                    "analyzer": "ik_smart",

                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "url": {
                    "type": "keyword",
                }
            }
        }
    }


class LoadEs(object):
    def __init__(self):
        self.es = Elasticsearch(hosts="http://localhost:9200")
        self.tmp_set = set()
        if not self.es.indices.exists(index='byr_articles'):
            self.es.indices.create(index='byr_articles', body=get_mapping())

    def process_item(self, fileName):
        i = 0
        for line in open(fileName, "r"):
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


def doLoadEs(fileName='byr_data.json'):
    load = LoadEs()
    load.process_item(fileName)


if __name__ == '__main__':
    doLoadEs(fileName='byr_data_merge.json')
