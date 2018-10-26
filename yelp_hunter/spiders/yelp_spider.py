# -*- coding: utf-8 -*-
import scrapy
import logging
from yelp_hunter.items import YelpHunterItem

s_url = 'https://www.yelp.com/search?find_desc=business+coach&find_loc=San+Francisco,+CA'

class YelpSpiderSpider(scrapy.Spider):
    name = 'yelp_spider'
    allowed_domains = ['www.yelp.com']
    start_urls = [s_url]


    def parse(self, response):
        links = response.css('h3.search-result-title>span>a::attr(href)').extract()
        for link in links:
            abs_url = response.urljoin(link)
            yield scrapy.Request(url=abs_url, callback = self.parse_indetail)


        # Follow pagination links
        next_page_url = response.css('div.arrange_unit > a.next::attr(href)').extract_first()
        if next_page_url:
            next_page_url = response.urljoin(next_page_url)
            yield scrapy.Request(url=next_page_url, callback=self.parse)
            logging.log(logging.WARNING, "Called next page")

    def parse_indetail(self, response):
            item = YelpHunterItem()
            b_name = response.css('h1.biz-page-title::text').extract_first()
            phone_number = response.css('span.biz-phone::text').extract_first()
            item["name"] = b_name.strip()
            item["phone"] = phone_number.strip()
            item["website"] = response.css('span.biz-website>a::text').extract_first()
            yield item