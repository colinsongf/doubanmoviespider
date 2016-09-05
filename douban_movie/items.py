# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field

class TagItem(Item):
	tag = Field()
	# 0 - not start, 1 - processing, 2 - finished
	state = Field()
	page = Field()

class DoubanMovieIdItem(Item):
	movie_id = Field()
	movie_url = Field()
	parsed = Field()
	movie_tag = Field()
	page = Field()

class DoubanMovieItem(Item):
    # 电视剧信息
	is_episode = Field()
	episode_num = Field()
	
	#电影ID
	movie_id = Field()
	#电影名称
	movie_name = Field()
	#电影评星
	movie_rate = Field()
	#电影评分人数
	movie_rate_people = Field()
	#看过人数
	movie_seen = Field()
	#想看人数
	movie_wishes = Field()
	#电影上映年份
	movie_year = Field()
	#电影首映时间
	movie_initial_release_date = Field()
	#电影导演
	movie_director = Field()
	#电影编辑
	movie_writor = Field()
	#电影演员
	movie_actors = Field()
	#电影类型
	movie_type = Field()
	#制片国家/地区
	movie_region = Field()
	#电影语言
	movie_language = Field()
	#电影时长，电视剧则为单集时长
	movie_time = Field()
	#电影别名
	movie_dialect = Field()
	#电影描述
	movie_desc = Field()
	#热门短评
	movie_hot_short_comments = Field()
	#电影标签
	movie_tags = Field()
	#电影图片链接
	movie_pic_url = Field()
