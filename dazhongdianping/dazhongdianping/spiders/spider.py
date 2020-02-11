# -*- coding: utf-8 -*-
import scrapy
from dazhongdianping.items import DazhongdianpingItem


class DaZhongDianPingSpider(scrapy.Spider):
    name = 'dazhongspider'
    allowed_domains = ['dianping.com']
    start_urls = ['http://www.dianping.com/beijing/ch10']

    def parse(self, response):
        # 获取店面的URL
        data_urls = response.xpath('//div[@id="shop-all-list"]/ul/li/div[@class="pic"]/a/@href').getall()
        for url in data_urls:
            print(url)
            # yield scrapy.Request(url, callback=self.shop_infos)
            yield {'url': url}

        # 翻页
        page_urls = response.xpath('//div[@class="page"]/a[@class="PageLink"]/@href').getall()
        for url in page_urls:
            yield scrapy.Request(url, callback=self.parse)

        # 地域区间
        regional_urls = response.xpath('//div[@class="navigation"]//a/@href').getall()
        for url in regional_urls:
            yield scrapy.Request(url, callback=self.parse)

    def shop_infos(self, response):
        # 店面详情页的信息
        # print(response.body.decode('utf-8'))
        # 获取店名
        shop_name = response.xpath('//h1/text()').get()
        # 获取星级
        shop_star = response.xpath('//div[@class="brief-info"]/span/@title').get()
        # 获取评论数
        shop_comment = response.xpath('//span[@id="reviewCount"]//text()').getall()
        # 获取地址
        shop_addr = response.xpath('//span[@id="address"]//text()').getall()
        items = DazhongdianpingItem(name=shop_name, star=shop_star, comment=shop_comment, addr=shop_addr)
        yield items
