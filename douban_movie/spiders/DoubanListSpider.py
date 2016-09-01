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
from bitarray import bitarray
from pymongo import MongoClient

# pattern define
lang_pattern_str =  ".*语言:</span> (.+?)<br>".decode("utf8")
region_pattern_str = ".*制片国家/地区:</span>(.+?)<br>".decode("utf8")
dialect_pattern_str = ".*又名:</span>(.+?)<br>".decode("utf8")

language_pattern = re.compile(lang_pattern_str,re.S)
region_pattern = re.compile(region_pattern_str,re.S)
dialect_pattern = re.compile(dialect_pattern_str,re.S)
# end pattern define

tag_year = 2016
failed_count = 0
parse_count = 0
real_parse_count = 0
#used to restart crawler
parsedids = bitarray(100000000)
parsedids.setall(False)

class DoubanListSpider(CrawlSpider):
	name = "doubanlist"
	allowed_domain = ["movie.douban.com"]
	
	tag_url  = "https://movie.douban.com/tag/"
	# use tag to crawl movie data
	start_urls = [
		"https://movie.douban.com/tag/2016"
	]
	
	def __init__(self,*a,**kw):
		super(DoubanListSpider,self).__init__(*a,**kw)
		self.client = MongoClient()
		self.db = self.client.movie
		self.movies = self.db.movie_test
		
		idstr = self.movies.find({},{'movie_id':1})
		print("restart crawler, already mined %d movies"%(idstr.count()))
		for ids in idstr:
			id = int(ids["movie_id"])
			parsedids[id] = True
		print("Go!")
	
	def parse(self, response):
		global parse_count
		global tag_year
		global parsedids
		this_page = response.xpath('//span[@class="thispage"]/text()').extract_first()
		pages = response.xpath('//div[@class="article"]//tr[@class="item"]//a[@class="nbg"]/@href').extract()
		if pages:
			id_count = 0
			for page in pages:
				page_id = int(page.split('/')[-2])
				id_count += 1
				if parsedids[page_id]:
					continue
				else:
					parse_count += 1
					parsedids[page_id] = True
					print("parsing year %d, with page number %s with count = %d and url = %s"%(tag_year,this_page,id_count,page))
					print("parse count = %d"%(parse_count))
					yield Request(page,callback = self.parse_item)
					
		#find next page
		nextpage = response.xpath('//span[@class="next"]/a/@href').extract_first()
		if nextpage:
			print("go to next page")
			yield Request(nextpage,callback=self.parse)
		else:
			# no next page
			if tag_year >= 1940:	
				print("no next page, parsing next year %d"%(tag_year-1))
				tag_year -= 1
				next_url = self.tag_url+str(tag_year)
				yield Request(next_url,callback=self.parse)
	
	def add_array(self,name,arr,item):
		item[name]=[]
		for x in arr:
			item[name].append(x.strip())

	def parse_item(self, response):
		global failed_count
		global real_parse_count
		item = DoubanMovieItem()
		try:
			real_parse_count += 1
			print("real parse count = %d"%(real_parse_count))
			# get movie id
			url = response.url
			id = url.split('/')[-2].strip() 
			item["movie_id"] = id
			
			# get movie name
			name = response.xpath('//div[@id="content"]/h1/span[1]/text()').extract_first()
			item["movie_name"] = name.strip() if name else ""
			
			#get movie year
			year = response.xpath('//div[@id="content"]/h1/span[2]/text()').extract_first()
			item["movie_year"] = year.strip("（）() ") if year else ""
			
			# get movie rate
			rate = response.xpath("//div[@class='rating_self clearfix']/strong/text()").extract_first()
			item["movie_rate"] = float(rate.strip() if rate else "-1")
			
			# get movie rate people
			rate_num = response.xpath("//span[@property='v:votes']/text()").extract_first()
			item["movie_rate_people"] = int(rate_num.strip() if rate_num else "-1")
			
			# get hot short comments
			comments = response.xpath("//div[@id='hot-comments']//div[@class='comment-item']//div[@class='comment']/p/text()").extract()
			votes = response.xpath("//div[@id='hot-comments']//div[@class='comment-item']//div[@class='comment']//span[@class='votes pr5']/text()").extract()
			rates = response.xpath("//div[@id='hot-comments']//div[@class='comment-item']//span[@class='comment-info']/span[1]/@title").extract()
			if len(comments) == len(votes) and len(votes) == len(rates):
				commentsarray = []
				for i in range(len(votes)):
					short_comments = {}
					short_comments['comment'] = comments[i]
					short_comments['votes'] = int(votes[i])
					short_comments['rates'] = rates[i]
					commentsarray.append(short_comments)
				item["movie_hot_short_comments"] = commentsarray
			
			seenwish = response.xpath("//div[@class='subject-others-interests-ft']//a//text()").extract()
			if seenwish and len(seenwish) == 2:
				item['movie_seen'] = int(seenwish[0][:-3])
				item['movie_wishes'] = int(seenwish[1][:-3])
			
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
			item["movie_time"] = float(time.strip() if time else "-1")
			
			types = info.xpath("span[@property='v:genre']/text()").extract()
			self.add_array("movie_type",types,item)
			
			try:
				lang = re.search(language_pattern,infostr)
				if lang:
					language = lang.group(1).strip()
					item["movie_language"] = language.strip()
			except:
				pass

			try:
				regionmatch = re.search(region_pattern,infostr)
				if regionmatch:
					region = regionmatch.group(1).strip()
					item["movie_region"] = region.strip()
			except:
				pass
			
			try:
				dialectmatch = re.search(dialect_pattern,infostr)
				if dialectmatch:
					dialect = dialectmatch.group(1).strip()
					item["movie_dialect"] = dialect.strip()
			except:
				pass

			desc = response.xpath("//span[@property='v:summary']/node()").extract_first().strip()
			item["movie_desc"] = desc.strip() if desc else ""
			
			tags = response.xpath("//div[@class='tags-body']/a/text()").extract()
			self.add_array("movie_tags",tags,item)
			
			pic = response.xpath("//div[@id='mainpic']/a/img/@src").extract_first()
			item["movie_pic_url"] = pic
			
			yield item
			
		except Exception,e:
			# do nothing
			logging.info("Parse error:%s"%(str(e)))
			print("failed_count = %d"%(failed_count+1))
			failed_count += 1
			pass
