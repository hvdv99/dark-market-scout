from crawler.crawler import Crawler

# configuring the crawler
crawl_scout = Crawler()
crawl_scout.set_seed('')
crawl_scout.set_cookies([''])
crawl_scout.set_exit_condition(crawl_scout.requests_send_counter <= 3)
crawl_scout.set_request_timing_behaviour(3)

# start crawling
crawl_scout.crawl()
