import json
import re


def unique(list):
    key_exactor = lambda item: (item['id'], item['article_contents'])

    key_set = set()
    ret = []
    for item in list:
        key = key_exactor(item)
        if key not in key_set:
            key_set.add(key)
            ret.append(item)
    return ret


def merge(old_item, new_item):
    key = lambda item: (item['pos'], item['article_contents'])

    new_articles = unique(new_item["articles"], key) or []
    old_articles = unique(old_item["articles"], key) or []
    all_articles = old_articles + new_articles
    all_articles.sort(key=key)
    all_articles = unique(all_articles, key)
    new_item["articles"] = all_articles
    return new_item


class MergeFile(object):
    def __init__(self):
        self.id = 0
        self.data_dict = dict()

    def process_item(self, item):
        item_dict = dict(item)
        results = re.findall('https://bbs.byr.cn/#!article/(.*?)/(\d+)', item['url'])
        item_id = results[0][0] + results[0][1]
        if item['url'] not in self.data_dict:
            self.data_dict[item['url']] = item_dict
            self.id += 1
        else:
            old = self.data_dict[item['url']]
            item_dict = merge(old, item_dict)
            self.data_dict[item['url']] = item_dict

        return item

    def save_data(self):
        with open("byr_data_merge.json", "w") as outfile:
            for value in self.data_dict.values():
                outfile.write(json.dumps(value, ensure_ascii=False) + "\n")


if __name__ == '__main__':

    mergeFile = MergeFile()

    with open("byr_data_merge.json", "r") as infile:
        for line in infile:
            item = json.loads(line)
            mergeFile.process_item(item)

    with open("byr_data.json", "r") as infile:
        for line in infile:
            item = json.loads(line)
            mergeFile.process_item(item)

    mergeFile.save_data()
