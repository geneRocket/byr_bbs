import re

from elasticsearch import Elasticsearch


es = Elasticsearch()
# dsl = {
#     "query": {
#         "multi_match": {
#             "query": "互联网应用",
#             "fields": ["title", "articles.article_contents"]
#         }
#     }
# }
# result = es.search(index='bbs_articles', body=dsl)
# print(result)

# result = es.indices.delete(index='bbs_articles_demo', ignore=[400, 404])
if not es.indices.exists('bbs_articles_demo'):
    print('索引不存在')

# url = 'https://bbs.byr.cn/#!article/SA/62136'
# results = re.findall('https://bbs.byr.cn/#!article/(.*?)/(\d+)', url)
# print(results[0][0] + results[0][1])
