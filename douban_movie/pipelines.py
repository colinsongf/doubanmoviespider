# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime
import json
import logging
from pymongo import MongoClient

client = MongoClient()
db = client.movie
movies = db.movies_info
movie_id_list = db.id_list

class DoubanMovieIdListPipelineWithMongoDB(object):
	def process_item(self,item,spider):
		global movie_id_list
		if spider.name != "doubanidlist":
			return
		try:
			movie_id_list.insert_one(dict(item))
		except Exception,e:
			print Exception,":",e
			pass
			
class DoubanMoviePipelineWithMongoDB(object):	
	def process_item(self,item,spider):
		global movies
		if spider.name != "doubanlist":
			return
		try:
			ret = movies.find_one({"movie_id":item['movie_id']})
			if ret:
				logging.info("Movie %s to database with id %s is already in database"%(item['movie_name'],item['movie_id']))
				pass
			else:
				movie_id_list.find_one_and_update({'movie_id':item['movie_id']},{'$set':{'parsed':True}})
				movies.insert_one(dict(item))
				logging.info("Added movie %s to database with id %s"%(item['movie_name'],item['movie_id']))
		except Exception,e:
			print("error when insert movie %s with id %s"%(item['movie_name'],item['movie_id']))
			print Exception,":",e


			