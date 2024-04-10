from elasticsearch import Elasticsearch

es = Elasticsearch(hosts="http://localhost:9200")


def get_demo():
    word = "进了职场，我是真的讨厌和女性打交流"

    dsl = {
        "query": {

            "bool": {
                "filter": [
                    {"term": {"title.keyword": word}}
                ]
            }
        },

        "from": 0, "size": 200,

    }

    result = es.search(index='byr_articles', body=dsl)
    for item in result["hits"]["hits"]:
        text = ''
        for article in item['_source']['articles']:
            text = (text + "\n" + '=' * 20 + '\n' + article['article_contents'])
        print(item["_source"]["title"], item["_source"]["url"])
        print(text)


get_demo()
