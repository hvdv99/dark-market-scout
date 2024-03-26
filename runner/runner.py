from crawler.crawler import Crawler
from config import constants as c

# configuring the crawler
crawl_scout = Crawler()
crawl_scout.set_seed(c.SEED)
crawl_scout.set_cookies(c.COOKIES)
crawl_scout.set_max_pages_to_crawl(5)
crawl_scout.set_request_interval(1)
crawl_scout.set_user_agent_behaviour(15)  # after how many requests the user agent will be replaced for new one
crawl_scout.set_request_timing_behaviour(new_timing_behaviour='')  # default: 'constant' or set to 'random'
crawl_scout.set_resource_dir('')  # set to name of the marketplace that's being scraped

# start crawling
crawl_scout.crawl()
