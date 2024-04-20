from crawler.crawler import Crawler
from config import constants as c

# Instantiate object
crawl_scout = Crawler()

# Name of resource directory is required
crawl_scout.set_resource_dir('nexus')  # set to name of the marketplace that's being scraped

# Synchronizing resources setting
crawl_scout.synchronize = True
crawl_scout.synchronize_resources()

# configuring the crawler
# crawl_scout.set_seed('')
crawl_scout.set_cookies(c.COOKIES)
crawl_scout.set_max_pages_to_crawl(200)
crawl_scout.set_request_timing((2, 5))  # time between each request
crawl_scout.set_user_agent_behaviour(3)  # after how many requests the user agent will be replaced for new one

# start crawling
# crawl_scout.crawl()
