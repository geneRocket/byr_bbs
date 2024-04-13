import json

from elasticsearch import Elasticsearch

es = Elasticsearch(hosts="http://localhost:9200")


def search_demo():
    words = ["北邮"]

    dsl = {
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "should": [

                        ],
                        "filter": [
                            {
                                "range": {
                                    'reply_time': {
                                        # 'gte': '2020-06-01'
                                    }
                                }
                            }

                        ],
                    }
                },
                "functions": [
                    {
                        "script_score": {
                            "script": {
                                "source": "Math.log10(2+(doc['articles.voteup_count'].sum()))",
                                "lang": "painless"
                            },
                        },
                        "weight": 1
                    },
                    {
                        "field_value_factor": {
                            "field": "reply_count",
                            "modifier": "log2p",  # ln2p，log2p
                            "factor": 0.5
                        },
                        "weight": 1
                    },
                ],
                "score_mode": "sum",
                "boost_mode": "multiply",
                "max_boost": 3
            },

        },

        "sort": {
            "_score": {"order": "desc"},
            "articles.voteup_count": {
                "mode": "sum",
                "order": "desc",
            },
            "reply_count": {
                "order": "desc",
            },

        },
        "from": 0, "size": 20,

    }

    for word in words:
        condition = dsl["query"]["function_score"]["query"]["bool"]["should"]
        condition.append(
            {"match": {"title": {"query": word, "boost": 20}}})
        condition.append(
            {"match": {"articles.article_contents": {"query": word, "boost": 10}}})
        condition.append(
            {"wildcard": {"title": {"value": "*{}*".format(word), "boost": 40}}})
        condition.append(
            {"match_phrase": {"articles.article_contents": {"query": word, "boost": 30}}})
        condition.append({"wildcard": {"title.keyword": '*' + word + '*'}})

    not_use_voteup_count = False
    if not_use_voteup_count:
        dsl["query"]["function_score"]["functions"] = None

    explain = False
    if explain:
        dsl["explain"] = True
        dsl["size"] = 2
    result = es.search(index='byr_articles', body=dsl)
    if explain:
        print(json.dumps(result.body, ensure_ascii=False))

    for item in result["hits"]["hits"]:
        text = ''
        key = lambda item: (int(item['voteup_count']))
        item['_source']['articles'].sort(key=key, reverse=True)
        cnt = 0
        for article in item['_source']['articles']:
            if (int(article['voteup_count']) == 0):
                break
            if "【 在 " in article['article_contents']:
                article['article_contents'] = article['article_contents'][:article['article_contents'].find("【 在 ")]
            article['article_contents'] = article['article_contents'].replace("\n", "")
            text += article['voteup_count'] + " " + article['article_contents'] + "\n"
            cnt += 1
            if cnt > 5:
                break
        print('=' * 40)
        print(item["_source"]["title"], item["_source"]["url"], item["sort"])
        print(text)



search_demo()
