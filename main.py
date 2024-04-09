import os

from scrapy import cmdline

if not os.path.exists("byr_data.json"):
    with open("byr_data.json", "a+") as _:
        pass

if not os.path.exists("byr_data_merge.json"):
    with open("byr_data_merge.json", "a+") as _:
        pass

cmdline.execute("scrapy crawl board_spider".split())