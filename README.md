# Douban Movie Spider

Use scrapy to download movie info from douban movie

## How to use

- Create a mongodb database movie and collections movies
- Or you can use mysql database, but need to change the setting.py to use mysql database
- Run cmd in linux: scrapyq crawl douban --logfile = [logfilename] -s JOBDIR=[resume dir] &
- You can change the number in spider to download more movies
