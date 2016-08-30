# Douban Movie Spider

Use scrapy to download movie info from douban movie

this tool is still under development, so bellowing instructions may be changed over time.

## How to use

- Create a mongodb database movie and collections movies
- Or you can use mysql database, but need to change the setting.py to use mysql database
- Run cmd in linux: scrapyq crawl douban --logfile = [logfilename] -s JOBDIR=[resume dir] &
- You can change the number in spider to download more movies

## Useful links to understand these code
- Sample code of cn blogs(framework): https://github.com/jackgitgz/CnblogsSpider
- Sample code of douban movie: http://www.cnblogs.com/Shirlies/p/4536880.html
- Prevent spider to be ban(only use header): http://www.tuicool.com/articles/VRfQR3U
- Useful website for regex(some information can't parse by xpath): https://regex101.com/#python
- Scrapy(spider): http://doc.scrapy.org/en/1.0/intro/overview.html
- MongoDB(database used): http://www.runoob.com/mongodb/mongodb-tutorial.html
- Python API for MongoDB(connect to mongodb): https://docs.mongodb.com/getting-started/python/
- Xpath(parse the web page): http://www.w3schools.com/xsl/xpath_intro.asp

## To-do
- Can't parse televation information
- Slow, try to use proxy
- Use bit array to store crawled information
