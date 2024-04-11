import json
import re


def unique(item_list):
    key_exactor = lambda item: (item['id'], item['article_contents'])

    key_dict = dict()
    for item in item_list:
        key = key_exactor(item)
        if key not in key_dict:
            key_dict[key] = item
        else:
            key_dict[key]["voteup_count"] = max(key_dict[key]["voteup_count"], item["voteup_count"])
            key_dict[key]["votedown_count"] = max(key_dict[key]["votedown_count"], item["votedown_count"])
    ret = list(key_dict.values())
    return ret


def merge(old_item, new_item):
    key = lambda item: (item['pos'], item['article_contents'])

    new_articles = new_item["articles"] or []
    old_articles = old_item["articles"] or []
    all_articles = old_articles + new_articles
    all_articles = unique(all_articles)
    all_articles.sort(key=key)
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
            self.data_dict[item['url']] = merge(item_dict, item_dict)
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

    try:
        with open("byr_data.json", "r") as infile:
            for line in infile:
                item = json.loads(line)
                mergeFile.process_item(item)
    except FileNotFoundError:
        pass

    mergeFile.save_data()
