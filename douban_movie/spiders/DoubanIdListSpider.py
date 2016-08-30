# -*- coding: utf-8 -*-
import sys
reload(sys)

sys.setdefaultencoding("utf-8")

from scrapy.spiders import CrawlSpider,Rule
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.linkextractors import LinkExtractor
from douban_movie.items import DoubanMovieIdItem
import logging
from bitarray import bitarray

tag_year = 2016

#used to restart crawler
parsed_ids = bitarray(100000000)
parsed_ids.setall(False)

class DoubanListSpider(CrawlSpider):
	name = "doubanidlist"
	allowed_domain = ["movie.douban.com"]
	
	tag_url  = "https://movie.douban.com/tag/"
	# use tag to crawl movie data
	start_urls = [
		"https://movie.douban.com/tag/2016"
	]
	
	
	def parse(self, response):
		global parse_count
		global tag_year
		global parsed_ids
		this_page_num = response.xpath('//span[@class="thispage"]/text()').extract_first()
		pages = response.xpath('//div[@class="article"]//tr[@class="item"]//a[@class="nbg"]/@href').extract()
		add_count = 0
		if pages:
			for page in pages:
				page_id = int(page.split('/')[-2])
				if parsed_ids[page_id]:
					print("exist id = %s"%(page))
					continue
				else:
					add_count += 1
					item = DoubanMovieIdItem()
					parsed_ids[page_id] = True
					item['movie_id'] = page_id
					item['movie_url'] = page
					item['parsed'] = False
					yield item
		
		print("parsed %d items in year %d and page %s"%(add_count,tag_year,this_page_num))
		#find next page
		nextpage = response.xpath('//span[@class="next"]/a/@href').extract_first()
		if nextpage:
			print("go to next page %s"%(nextpage))
			yield Request(nextpage,callback=self.parse)
		else:
			# no next page
			if tag_year >= 1900:	
				print("no next page, parsing next year %d"%(tag_year-1))
				tag_year -= 1
				next_url = self.tag_url+str(tag_year)
				yield Request(next_url,callback=self.parse)
	
