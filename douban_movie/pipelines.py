# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
import MySQLdb.cursors
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
	
class DoubanMoviePipelineWithMySQL(object):
	def __init__(self):
		self.db = MySQLdb.connect("localhost","root","root","movie")
		
	def process_item(self, item, spider):
		now = datetime.utcnow().replace(microsecond=0).isoformat(' ')
		cursor = self.db.cursor()
		sql = "SELECT 1 FROM movie_tb WHERE movie_id = %s"%(item["movie_id"])
		
		'''
		strs = json.dumps(dict(item))
		o = open('tmp','w')
		o.write(strs)
		'''
		
		try:
			cursor.execute(sql)
			ret = cursor.fetchone()
			if ret:
				print("already in database")
				pass
			else:
				insert = "INSERT INTO movie_tb(movie_id,movie_json) VALUES('%s','%s')" %(item["movie_id"],json.dumps(dict(item)))
				cursor.execute(insert)
				self.db.commit()
		except Exception,e:
			print("error when insert movie %s with id %s"%(item['movie_name'],item['movie_id']))
			print Exception,":",e
			self.db.rollback()
		logging.info("Added movie %s to database with id %s"%(item['movie_name'],item['movie_id']))
