from crawler.crawler import Crawler
from config import constants as c

# Instantiate object
crawl_scout = Crawler()

# Synchronizing resources setting
crawl_scout.synchronize = True

# configuring the crawler
crawl_scout.set_resource_dir('nexus')  # set to name of the marketplace that's being scraped
crawl_scout.synchronize_resources()
# crawl_scout.set_seed(
#     'http://nexusabcdkq4pdlubs6wk6ad7pobuupzoomoxi6p7l32ci4vjtb2z7yd.onion/products/1e9c917e808c184d3f88c73869aa3459a623'
# )
# crawl_scout.set_cookies(c.COOKIES)
# crawl_scout.set_max_pages_to_crawl(200)
# crawl_scout.set_request_interval(5)  # time between each request
# crawl_scout.set_request_timing_behaviour(new_timing_behaviour='random')  # default: 'constant' or set to 'random'
# crawl_scout.set_user_agent_behaviour(3)  # after how many requests the user agent will be replaced for new one
#
# # start crawling
# crawl_scout.crawl()
