from crawler.crawler import Crawler
from config import constants as c

# configuring the crawler
crawl_scout = Crawler()
crawl_scout.set_seed(c.seed)
crawl_scout.set_cookies(c.cookies)
crawl_scout.set_max_pages_to_crawl(200)
crawl_scout.set_request_timing_behaviour('random')
crawl_scout.set_resource_dir('redbull market')

# start crawling
crawl_scout.crawl()
