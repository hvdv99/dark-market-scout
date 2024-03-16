from crawler.crawler import Crawler
from config import constants as c

# configuring the crawler
crawl_scout = Crawler()
crawl_scout.set_seed(c.seed)
crawl_scout.set_cookies(c.cookies)
crawl_scout.set_exit_condition(crawl_scout.requests_send_counter <= 3) # TODO - Change this because it does not work
crawl_scout.set_request_timing_behaviour(3)

# start crawling
crawl_scout.crawl()
