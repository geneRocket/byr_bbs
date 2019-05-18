from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware
from byr_bbs.middlewares.resources import USER_AGENT_LIST

import random


class RandomUserAgent(UserAgentMiddleware):
    def process_request(self, request, spider):
        user_agent = random.choice(USER_AGENT_LIST)
        request.headers.setdefault('User-Agent', user_agent)
