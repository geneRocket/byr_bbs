from elasticsearch import Elasticsearch

es = Elasticsearch()
dsl = {
    "query": {
        "multi_match": {
            "query": "互联网应用",
            "fields": ["title", "articles.article_contents"]
        }
    }
}
result = es.search(index='bbs_articles', body=dsl)
print(result)
