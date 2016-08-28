# -*- coding: utf-8 -*-
import sys
reload(sys)

sys.setdefaultencoding("utf-8")

from scrapy.spiders import CrawlSpider,Rule
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.linkextractors import LinkExtractor
from douban_movie.items import DoubanMovieItem
import re
import logging

lang_pattern_str =  ".*语言:</span> (.+?)<br>".decode("utf8")
region_pattern_str = ".*制片国家/地区:</span>(.+?)<br>".decode("utf8")
dialect_pattern_str = ".*又名:</span>(.+?)<br>".decode("utf8")

language_pattern = re.compile(lang_pattern_str,re.S)
region_pattern = re.compile(region_pattern_str,re.S)
dialect_pattern = re.compile(dialect_pattern_str,re.S)

count = 0

class DoubanSpider(CrawlSpider):
	name = "douban"
	allowed_domain = ["movie.douban.com"]
	start_urls = [
		"https://movie.douban.com/subject/25662337", # current famous movie
		"https://movie.douban.com/subject/1292052/", # classical movie
		"https://movie.douban.com/subject/1291561/", # cartoon
		"https://movie.douban.com/subject/26322792/", # love
		"https://movie.douban.com/subject/25964071/", # comedy
		"https://movie.douban.com/subject/1889243/", # science
		"https://movie.douban.com/subject/26356789/", # not famous
		"https://movie.douban.com/subject/25870483/" # terror
	]
	
	#rules = [
	#	Rule(LinkExtractor(allow=('from=subject-page')),callback='parse_item',follow=True)
	#]
	
	def add_array(self,name,arr,item):
		item[name]=[]
		for x in arr:
			item[name].append(x.strip())
	
	def parse(self, response):
		global count
		if count == 1000000:
			return
		else:
			count += 1
		item = DoubanMovieItem()
		try:
			# get movie id
			url = response.url
			id = url.split('/')[-2].strip() 
			item["movie_id"] = id
			
			# get movie name
			name = response.xpath('//div[@id="content"]/h1/span[1]/text()').extract_first()
			item["movie_name"] = name.strip()
			
			#get movie year
			year = response.xpath('//div[@id="content"]/h1/span[2]/text()').extract_first()
			item["movie_year"] = year.strip("（）() ")
			
			# get movie rate
			rate = response.xpath("//div[@class='rating_self clearfix']/strong/text()").extract_first()
			item["movie_rate"] = float(rate.strip())
			
			# get movie info
			info = response.xpath("//div[@id='info']")
			infoarray = info.extract()
			infostr = ''.join(infoarray).strip()
			
			director = info.xpath("span[1]/span[2]/a/text()").extract()
			self.add_array("movie_director",director,item)
			
			writor = info.xpath("span[2]/span[2]/a/text()").extract()
			self.add_array("movie_writor",writor,item)
			
			actors = info.xpath("span[3]/span[2]/a/text()").extract()
			self.add_array("movie_actors",actors,item)
			
			time = info.xpath("span[@property='v:runtime']/@content").extract_first()
			item["movie_time"] = float(time.strip())
			
			types = info.xpath("span[@property='v:genre']/text()").extract()
			self.add_array("movie_type",types,item)
			
			lang = re.search(language_pattern,infostr)
			if lang:
				language = lang.group(1).strip()
				item["movie_language"] = language.strip()
			
			regionmatch = re.search(region_pattern,infostr)
			if regionmatch:
				region = regionmatch.group(1).strip()
				item["movie_region"] = region.strip()
			
			dialectmatch = re.search(dialect_pattern,infostr)
			if dialectmatch:
				dialect = dialectmatch.group(1).strip()
				item["movie_dialect"] = dialect.strip()
			
			desc = response.xpath("//div[@id='link-report']/span[1]/text()").extract_first().strip()
			item["movie_desc"] = desc.strip()
			
			tags = response.xpath("//div[@class='tags-body']/a/text()").extract()
			self.add_array("movie_tags",tags,item)
			
			pic = response.xpath("//div[@id='mainpic']/a/img/@src").extract_first()
			item["movie_pic_url"] = pic
		
			
			yield item
		
			next_pages = response.xpath("//div[@class='recommendations-bd']/dl/dd/a/@href").extract()
			if next_pages:
				for page in next_pages:
					yield Request(page,callback = self.parse)
		except Exception,e:
			# do nothing
			logging.info("Parse error:%s"%(str(e)))
			pass