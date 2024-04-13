from crawler.crawler import Crawler
from config import constants as c

# Instantiate object
crawl_scout = Crawler()

# Synchronizing resources
crawl_scout.sync_resources()

# configuring the crawler
crawl_scout.set_seed(c.SEED)
crawl_scout.set_cookies(c.COOKIES)
crawl_scout.set_max_pages_to_crawl(10)
crawl_scout.set_request_interval(0)
crawl_scout.set_user_agent_behaviour(15)  # after how many requests the user agent will be replaced for new one
crawl_scout.set_request_timing_behaviour(new_timing_behaviour='constant')  # default: 'constant' or set to 'random'
crawl_scout.set_resource_dir('digital-thrift-shop')  # set to name of the marketplace that's being scraped

# start crawling
# crawl_scout.crawl()
