# -*- coding: utf-8 -*-
import json
import re
from copy import deepcopy

import scrapy

from byr_bbs.items import BoardItem, ArticleItem
from .bbs_config import HEADERS, LOGIN_FORM_DATA


class BoardSpiderSpider(scrapy.Spider):
    name = 'board_spider'
    allowed_domains = ['byr.cn']
    start_urls = ['https://bbs.byr.cn/index']
    replace_dict = {
        "&nbsp;": " ",
        "<br/>": "\n",
        "<br />": "\n",
        "<br/><br/>": "\n",
        "<br>--": "",
        "&gt;": ">",
        "_&lt;": "<",
    }
    filter_pattern = re.compile('|<img border="[\S]*" src="[\S]*" alt="[\S]*" class="[\S]*" title="[\S]*"/>'
                                '|<span class="emoji" style=".*".*</span>'
                                '|<img src=".*" alt=".*" style=".*"/>')

    re_replace_dict = [
        (
            re.compile(r'<a target="_blank" href="([\S]*)">单击此查看原图(([\S]*))</a>'),
            r' https://bbs.byr.cn/\1 '
        ),
        (
            re.compile(r'<a href="(.*)" target="_blank" <font color=".*">附件.*</font>.*</a>'),
            r' https://bbs.byr.cn/\1 '
        ),
        (
            re.compile(r'<a target=".*" href="(.*)".*</a>'),
            r' \1 '
        )
    ]

    def start_requests(self):
        try:
            yield scrapy.Request(
                url='https://bbs.byr.cn/index',
                meta={'cookiejar': 1},
                callback=self.post_login
            )
        except:
            print(">>>>>>>>>>>>>> Proxy not reachable")

    def post_login(self, response):
        yield scrapy.FormRequest.from_response(
            response,
            url='https://bbs.byr.cn/user/ajax_login.json',
            meta={'cookiejar': response.meta['cookiejar']},
            headers=HEADERS,
            formdata=LOGIN_FORM_DATA,
            callback=self.after_login
        )

    def after_login(self, response):
        yield scrapy.Request(
            url='https://bbs.byr.cn/n/b/section.json',
            meta={'cookiejar': response.meta['cookiejar']},
            callback=self.parse_board
        )

    def parse_board(self, response):
        json_dict = json.loads(response.body.decode('utf8'))
        json_boards = json_dict['data']['boards'][1:]
        for json_board in json_boards:
            for child_board in json_board['children']:
                item = BoardItem()
                if len(child_board['children']) == 0:
                    item['board_name'] = child_board['name']
                    item['board_url'] = 'https://bbs.byr.cn/n/board/' + child_board['id']
                    item['parent_section'] = json_board['name']
                    yield scrapy.Request(
                        url='https://bbs.byr.cn/n/b/board/' + child_board['id'] + '.json?page=1',
                        meta={
                            'cookiejar': response.meta['cookiejar'],
                            'id': child_board['id']
                        },
                        callback=self.parse_article_url
                    )
                for grandchild_board in child_board['children']:
                    item['board_name'] = grandchild_board['name']
                    item['board_url'] = 'https://bbs.byr.cn/n/board/' + grandchild_board['id']
                    item['parent_section'] = json_board['name']
                    yield scrapy.Request(
                        url='https://bbs.byr.cn/n/b/board/' + child_board['id'] + '.json?page=1',
                        meta={
                            'cookiejar': response.meta['cookiejar'],
                            'id': child_board['id']
                        },
                        callback=self.parse_article_url
                    )

    def parse_article_url(self, response):
        json_dict = json.loads(response.body.decode('utf8'))
        total_page = json_dict['data']['pagination']['total']
        current_page = json_dict['data']['pagination']['current']
        post_list = json_dict['data']['posts']
        for post in post_list:
            item = ArticleItem()
            item['title'] = post['title']
            item['poster'] = post['poster']
            item['gid'] = post['gid']
            item['url'] = 'https://bbs.byr.cn/#!article/' + json_dict['data']['name'] + '/' + str(post['gid'])
            item['reply_time'] = post['replyTime']
            item['reply_count'] = post['replyCount']
            yield scrapy.Request(
                url='https://bbs.byr.cn/n/b/article/' + json_dict['data']['name'] + '/'
                    + str(post['gid']) + '.json?page=1',
                meta={
                    'item': deepcopy(item),
                    'name': json_dict['data']['name']
                },
                callback=self.parse_articles
            )
        # 翻页
        if current_page <= total_page:
            current_page += 1
            yield scrapy.Request(
                url='https://bbs.byr.cn/n/b/board/' + response.meta['id'] + '.json?page=' + str(current_page),
                meta={
                    'cookiejar': response.meta['cookiejar'],
                    'id': response.meta['id']
                },
                callback=self.parse_article_url
            )

    def parse_articles(self, response):
        json_dict = json.loads(response.body.decode('utf8'))
        total_page = json_dict['data']['pagination']['total']
        current_page = json_dict['data']['pagination']['current']
        article_list = json_dict['data']['articles']
        item = response.meta['item']
        articles = []
        for article in article_list:
            contents = dict()
            contents['id'] = article['poster']['id']
            contents['user_name'] = article['poster'].get('user_name', None)
            contents['time'] = article['time']
            article_content = article['content']
            for old in self.replace_dict:
                new = self.replace_dict[old]
                article_content = article_content.replace(old, new)
            article_content = self.filter_pattern.sub('', article_content)
            for (old, new) in self.re_replace_dict:
                article_content = old.sub(new, article_content)
            contents['article_contents'] = article_content
            contents['voteup_count'] = article['voteup_count']
            contents['votedown_count'] = article['votedown_count']
            contents['pos'] = article['pos']
            articles.append(contents)
        if (item.get('articles') is None):
            item['articles'] = []
        item['articles'] = item['articles'] + articles
        yield item

        # 翻页
        if current_page <= total_page:
            current_page += 1
            yield scrapy.Request(
                url='https://bbs.byr.cn/n/b/article/' + response.meta['name'] + '/'
                    + str(item['gid']) + '.json?page=' + str(current_page),
                meta={
                    'item': deepcopy(item),
                    'name': response.meta['name']
                },
                callback=self.parse_articles
            )
