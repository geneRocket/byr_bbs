from elasticsearch import Elasticsearch

es = Elasticsearch(hosts="http://localhost:9200")


def get_demo():
    author = ""

    dsl = {
        "query": {

            "bool": {
                "filter": [
                    {"term": {"articles.id": author}},
                ]
            }
        },
        "sort": {
            "articles.voteup_count": {
                "order": "desc",
            },
            "articles.time": {
                "order": "desc",
            },
        },

        "from": 0, "size": 200,

    }

    result = es.search(index='byr_articles', body=dsl)
    for item in result["hits"]["hits"]:
        text = ''
        for article in item['_source']['articles']:
            if article['id'] == author:
                if '【' in article['article_contents']:
                    article['article_contents'] = article['article_contents'][:article['article_contents'].find('【')]
                text = (text + "\n" + article['article_contents'])
        print(item["_source"]["title"], item["_source"]["url"])
        print(text)
        print('=' * 20)


get_demo()
