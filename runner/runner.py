from crawler.crawler import Crawler
from config import constants as c

# configuring the crawler
crawl_scout = Crawler()
crawl_scout.set_seed(c.seed)
crawl_scout.set_cookies(c.cookies)
crawl_scout.set_max_pages_to_crawl(3)
crawl_scout.set_request_interval(3)
crawl_scout.set_user_agent_behaviour(15)  # after how many requests the user agent will be replaced.
crawl_scout.set_request_timing_behaviour('random')
crawl_scout.set_resource_dir('kerberos')

# start crawling
crawl_scout.crawl()