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
                                "source": "Math.log1p(doc['articles.voteup_count'].sum())",
                                "lang": "painless"
                            }
                        },
                        "weight": 1
                    },
                    {
                        "field_value_factor": {
                            "field": "reply_count",
                            "modifier": "log1p",  # ln2p，log1p
                        },
                        "weight": 0.5
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
        "from": 0, "size": 200,

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
        print(item["_source"]["title"], item["_source"]["url"], item["sort"])



search_demo()
