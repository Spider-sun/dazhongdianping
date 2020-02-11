# -*- coding: utf-8 -*-
# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
USER_AGENTS_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586",
    "Mozilla/4.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/11.0.1245.0 Safari/537.36",
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533+ (KHTML, like Gecko) Element Browser 5.0',
    'Mozilla/5.0 (Windows; U; ; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.8.0',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; Avant Browser; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)',
    'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.8.1a2) Gecko/20060512 BonEcho/2.0a2',
    'Mozilla / 5.0（Macintosh; U; Intel Mac OS X 10.8; it; rv：1.93.26.2658）Gecko / 20141026 Camino / 2.176.223（MultiLang）（例如Firefox / 3.64.2268）0',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17',
    'Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.45 Safari/535.19',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0',
    'Mozilla/5.0 (Windows NT 6.1; rv:12.0) Gecko/20120403211507 Firefox/12.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko'
]


import random
import requests
import redis
import re


from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
        ConnectionRefusedError, ConnectionDone, ConnectError, \
        ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed

from scrapy.core.downloader.handlers.http11 import TunnelError


class Random_User_Agent_Middleware(object):
    '''随机请求头'''
    def process_request(self, request, spider):
        request.headers['user-agent'] = random.choice(USER_AGENTS_LIST)


class Proxy_Middleware(object):
    '''随机IP'''
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseFailed,
                           IOError, TunnelError)

    def process_request(self, request, spider):
        self.reids_pool = redis.Redis(host='127.0.0.1', port=6379)
        proxies = self.reids_pool.hgetall('proxies')
        keys = []
        for key in proxies.keys():
            keys.append(key.decode('utf-8'))
        proxy = random.choice(keys)
        request.meta['proxy'] = 'http://' + proxy
        return None

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
            ip = re.findall('http://(.*?:\d+)', request.meta['proxy'])[0]
            print(ip)
            self.reids_pool.hdel('proxies', ip)
            proxies = self.reids_pool.hgetall('proxies')
            keys = []
            for key in proxies.keys():
                keys.append(key.decode('utf-8'))
            proxy = random.choice(keys)
            print('更换ip' + proxy)
            request.meta['proxy'] = "http://" + proxy

    def process_response(self, request, response, spider):
        # 如果该ip不能使用，更换下一个ip
        if response.status != 200:
            ip = re.findall('http://(.*?:\d+)', request.meta['proxy'])[0]
            self.reids_pool.hdel('proxies', ip)
            proxies = self.reids_pool.hgetall('proxies')
            keys = []
            for key in proxies.keys():
                keys.append(key.decode('utf-8'))
            proxy = random.choice(keys)
            print('更换ip' + proxy)
            request.meta['proxy'] = "http://" + proxy
            return request
        return response


