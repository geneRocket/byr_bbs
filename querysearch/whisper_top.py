from elasticsearch import Elasticsearch

es = Elasticsearch(hosts="http://localhost:9200")


def get_demo():
    word = "网飞三体怎么样"

    dsl = {
        "query": {

            "bool": {
                "filter": [
                    {"wildcard": {"url": '*IWhisper*'}},
                    {
                        "range": {
                            'reply_time': {
                                'gte': '2024-04-09'
                            }
                        }
                    }
                ]
            }
        },
        "sort": {
            "articles.voteup_count": {
                "mode": "sum",
                "order": "desc",
            },
            "reply_count": {
                "order": "desc",
            },

        },

        "from": 0, "size": 2000,

    }

    result = es.search(index='byr_articles', body=dsl)
    for item in result["hits"]["hits"]:
        text = ''
        for article in item['_source']['articles']:
            text = (text + "\n" + '=' * 20 + '\n' + article['article_contents'])
        print(item["_source"]["title"], item["_source"]["url"], item["sort"])
        # print(text)


get_demo()
