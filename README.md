# Douban Movie Spider

Use scrapy to download movie info from douban movie

this tool is still under development, so bellowing instructions may be changed over time.

## Ideas
A common problem in spider is the spider has been shut down, and you need to restart the spider but you don't want the spider to re-crawl the website, so how to resume your spider is important.

One of the nice feature of douban movie is each movie has a unique id, so my basic idea is like this:

1. DoubanIdListSpider use tag to crawl movie ids, get a collection(movie_id_list) of movie ids. Each item contains id, url, if this movie has crawled, how many attempt times.

2. DoubanListSpider contain a bit array(100000000 elements) and initialize this bit array with movie_id_list to mark the downloaded movie ids. Get the un-crawled movie ids and start to crawl, and update the movie_id_list.

3. How to crawl by using serval machines?
   - use a remote mongodb to store movie_id_list, and each machine download it, and crawl part of it, after download, upadte the remote colletion

## How to use

- Create a mongodb database movie
- Run cmd in linux: scrapyq crawl doubanidlist --logfile = [logfilename] -s JOBDIR=[resume dir]
- If you restart the id list spider, change the setting FromDatabase to True(not done yet)
- Use doubanlist spider to crawl movie detail informations

## Useful links to understand these code
- Sample code of cn blogs: https://github.com/jackgitgz/CnblogsSpider
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
