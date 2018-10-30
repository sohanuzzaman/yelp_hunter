# -*- coding: utf-8 -*-
import scrapy
import logging
import re
from yelp_hunter.items import YelpHunterItem
from urllib.parse import urlparse

s_url = 'https://www.yelp.com/search?find_desc=Business+Coach&find_loc=New+York+City'


# Adding http in front of the website address
def add_http(website):
    if not website.startswith("http"):
        website = "http://" + website
        
    return website


# Checking if the link belongs to the correct website and correcting relative links
def validate_link(domain, link):
    if link.startswith('/'):
        abs_url = domain + link
        return abs_url
    elif link.startswith(domain):
        return domain
    else:
        return None


# Starting the spider logics
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


    #Scrapping detail information from the business address 
    def parse_indetail(self, response):
            item = YelpHunterItem()
            b_name = response.css('h1.biz-page-title::text').extract_first()
            phone_number = response.css('span.biz-phone::text').extract_first()
            website = response.css('span.biz-website>a::text').extract_first()
            item["name"] = b_name.strip()
            item["phone"] = phone_number.strip()
            item["website"] = website
            # email = parse_email(url=add_http(website))
            yield scrapy.Request(url=add_http(website), callback=self.parse_email, meta={'item': item, 'links': set(), 'emails': set()}, dont_filter=True)



    def parse_email(self, response):
            item = response.meta['item']
            # email = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", str(response.body), re.I)[0]
            # if email:
            #     item["email"] = email
            # else:
            links = response.meta['links']
            emails = response.meta['emails']

            # Constructing the url from the parsed page to aboid scraping other domains
            domain = urlparse(response.url)
            domain = domain.scheme + "://" + domain.netloc
            all_links = response.css('a::attr(href)').extract()
            
            # Getting all email address found in the webpage
            for found_address in re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", str(response.body), re.I):
                emails.add(found_address)

            # Parsing links to other pages of the website
            for link in all_links:
                url = validate_link(domain, link)
                links.add(url)

            # Check all the links in the website untill find an email address
            while len(links) > 0 and len(emails) < 1:
                link = links.pop()
                scrapy.Request(url=link, callback=self.parse_email, meta={'item': item, 'links': links, 'emails': emails}, dont_filter=True)
            
            # Finally add the result into output
            item["email"] = ",".join(emails)
            yield item
