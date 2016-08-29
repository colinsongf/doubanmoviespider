# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime
import json
import logging
from pymongo import MongoClient

class DoubanMoviePipelineWithMongoDB(object):
	def __init__(self):
		self.client = MongoClient()
		self.db = self.client.movie
		self.movies = self.db.movie_test
	
	def process_item(self,item,spider):
		try:
			ret = self.movies.find_one({"movie_id":item['movie_id']})
			if ret:
				logging.info("Movie %s to database with id %s is already in database"%(item['movie_name'],item['movie_id']))
				pass
			else:
				self.movies.insert_one(dict(item))
				logging.info("Added movie %s to database with id %s"%(item['movie_name'],item['movie_id']))
		except Exception,e:
			print("error when insert movie %s with id %s"%(item['movie_name'],item['movie_id']))
			print Exception,":",e
