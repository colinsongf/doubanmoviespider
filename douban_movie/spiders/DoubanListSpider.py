# -*- coding: utf-8 -*-
import sys
reload(sys)

sys.setdefaultencoding("utf-8")

from scrapy.spiders import CrawlSpider,Rule
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.linkextractors import LinkExtractor
from douban_movie.items import DoubanMovieItem,DoubanMovieIdItem
import re
import logging
from bitarray import bitarray
from pymongo import MongoClient

# pattern define
lang_pattern_str =  ".*语言:</span> (.+?)<br>".decode("utf8")
region_pattern_str = ".*制片国家/地区:</span>(.+?)<br>".decode("utf8")
dialect_pattern_str = ".*又名:</span>(.+?)<br>".decode("utf8")
episode_num_pattern_str = ".*集数:</span>(.+?)<br>".decode("utf8")
single_time_pattern_str = ".*单集片长:</span>(.+?)分钟".decode("utf8")

language_pattern = re.compile(lang_pattern_str,re.S)
region_pattern = re.compile(region_pattern_str,re.S)
dialect_pattern = re.compile(dialect_pattern_str,re.S)
episode_num_patter = re.compile(episode_num_pattern_str,re.S)
single_time_pattern = re.compile(single_time_pattern_str,re.S)
# end pattern define

failed_count = 0
parse_count = 0
real_parse_count = 0

#used to restart crawler
allids = bitarray(100000000)
parsedids = bitarray(100000000)
allids.setall(False)
parsedids.setall(False)

class DoubanListSpider(CrawlSpider):
	name = "doubanlist"
	allowed_domain = ["movie.douban.com"]
	
	 prefix_url  = "https://movie.douban.com/"
	
	# not used here
	start_urls = [
		"https://movie.douban.com/tag/2016"
	]
	
	def __init__(self,*a,**kw):
		super(DoubanListSpider,self).__init__(*a,**kw)
		self.client = MongoClient()
		self.db = self.client.movie
		self.ids = self.db.id_list
		
		allidslist = self.ids.find({},{'movie_id',1})
		print("all id number = %d"%(allidslist.count()))
		for idx in allidslist:
			allids[idx['movie_id']] = True
			
		minedids = self.ids.find({"parsed":True},{'movie_id':1})
		print("start crawler, already mined %d movies"%(minedids.count()))
		for id in minedids:
			parsedids[id['movie_id']] = True
		print("Go!")
	
	def parse(self, response):
		global parse_count
		global parsedids
		
		#response not used here, just use this method to start parse
		not_parsed_ids = self.ids.find({'parsed':False},{'movie_id':1})
		print("not mined movies %d"%(not_parsed_ids.count()))
		for id in not_parsed_ids:
			yield Request(prefix_url+str(id['movie_id']), callback = self.parse_item)
	
	def add_array(self,name,arr,item):
		item[name]=[]
		for x in arr:
			item[name].append(x.strip())

	def parse_item(self, response):
		global failed_count
		global real_parse_count
		item = DoubanMovieItem()
		try:
			is_episoder = False
			episodestr = response.xpath("//div[@class='episode_list']")
			if episodestr:
				is_episoder = True
			
			item['is_episode'] = is_episoder
			
			# get movie id
			url = response.url
			id = url.split('/')[-2].strip() 
			item["movie_id"] = int(id)
				
			# get movie name
			name = response.xpath('//div[@id="content"]/h1/span[1]/text()').extract_first()
			item["movie_name"] = name.strip() if name else ""
			
			print("mine movie %s with id %s"%(name,id))
			
			#get movie year
			year = response.xpath('//div[@id="content"]/h1/span[2]/text()').extract_first()
			item["movie_year"] = year.strip("（）() ") if year else ""
			
			# get movie rate
			rate = response.xpath("//div[@class='rating_self clearfix']/strong/text()").extract_first()
			item["movie_rate"] = float(rate.strip() if rate else "-1")
			
			# get movie rate people
			rate_num = response.xpath("//span[@property='v:votes']/text()").extract_first()
			item["movie_rate_people"] = int(rate_num.strip() if rate_num else "-1")
			
			# initial release date
			release_date = response.xpath("//span[@property='v:initialReleaseDate']/@content").extract_first()
			item['movie_initial_release_date'] = release_date
			
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
			
			#get seen and wish to see number
			seenwish = response.xpath("//div[@class='subject-others-interests-ft']//a//text()").extract()
			if seenwish:
				if len(seenwish) == 2:
					item['movie_seen'] = int(seenwish[0][:-3])
					item['movie_wishes'] = int(seenwish[1][:-3])
				if len(seenwish) == 3:
					item['movie_seen'] = int(seenwish[1][:-3])
					item['movie_wishes'] = int(seenwish[2][:-3])
			
			# get movie info
			info = response.xpath("//div[@id='info']")
			infoarray = info.extract()
			infostr = ''.join(infoarray).strip()
			
			#same region for movie and episode
			director = info.xpath("span[1]/span[2]/a/text()").extract()
			self.add_array("movie_director",director,item)
			
			writor = info.xpath("span[2]/span[2]/a/text()").extract()
			self.add_array("movie_writor",writor,item)
			
			actors = info.xpath("span[@class='actor']/span[2]/a/text()").extract()
			self.add_array("movie_actors",actors,item)

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
			#end same region
			
			if is_episoder:
				episodenummatch = re.search(episode_num_patter,infostr)
				if episodenummatch:
					episodenum = episodenummatch.group(1).strip()
					item["episode_num"] = int(episodenum)
				singletimematch = re.search(single_time_pattern,infostr)
				if singletimematch:
					singletime = singletimematch.group(1).strip()
					item["movie_time"] = float(singletime if singletime else "-1")
			else:
				item['episode_num'] = 1				
				time = info.xpath("span[@property='v:runtime']/@content").extract_first()
				item["movie_time"] = float(time.strip() if time else "-1")
			
			real_parse_count += 1
			print("real parse count = %d"%(real_parse_count))
			
			yield item
			
			# check if there is not mined ids
			next_pages = response.xpath("//div[@class='recommendations-bd']/dl/dd/a/@href").extract()
			if next_pages:
				for page in next_pages:
					idn = int(page.split('/')[-2])
					if allids[idn] = False:
					print("find new movie with id %d"%(idn))
						idItem = DoubanMovieIdItem()
						idItem["parsed"] = False
						idItem["movie_id"] = idn
						self.ids.insert(dict(idItem))
						allids[idn] = True
						
		except Exception,e:
			# do nothing
			logging.info("Parse error:%s"%(str(e)))
			print("failed_count = %d"%(failed_count+1))
			failed_count += 1
			pass
