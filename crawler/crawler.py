from fake_useragent import UserAgent
from collections import deque
import requests
from bs4 import BeautifulSoup

import os
import time
import random
import logging
import sys
from urllib.parse import urlparse, urljoin
import uuid


class Crawler:

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    def __init__(self):
        self.cookies = list()
        self.seed = str()
        self.proxies = {'http': 'socks5h://localhost:9050',
                        'https': 'socks5h://localhost:9050'}
        self.max_pages_to_crawl = None
        self.request_interval = 1  # the time between each request
        self.request_timing_behaviour = 'constant'  # defaults to constant, see: set_request_timing_behaviour()
        self.ua_behaviour = 1
        self.user_agent = None
        self.visited = set()
        self.queue = deque()
        self.requests_send_counter = int()
        self.resource_path = str()
        self.seed = set()
        self.exit_condition = bool()
        self.request_interval = 1
        self.request_timing = 'constant'


    def set_cookies(self, cookies: list):
        if not isinstance(cookies, list):
            raise TypeError('Cookies should be inserted as list')
        else:
            self.cookies = cookies

    def set_seed(self, seed: str):
        if not isinstance(seed, str):
            raise TypeError('Seed should string')
        self.seed = seed

    def set_max_pages_to_crawl(self, max_pages: int):
        if not isinstance(max_pages, int):
            raise TypeError('Condition is not of type bool')
        else:
            self.max_pages_to_crawl = max_pages

    def set_request_interval(self, new_interval: int):
        if not isinstance(new_interval, int):
            raise TypeError('Interval should be of type integer')
        if new_interval < 0:
            raise ValueError('Interval should be positive or zero')
        self.request_interval = new_interval

    def set_request_timing_behaviour(self, new_timing_behaviour: str):
        timing_types = {'constant', 'random'}
        if not isinstance(new_timing_behaviour, str):
            raise TypeError('Timing should be of type string')
        if new_timing_behaviour not in timing_types:
            raise ValueError('Timing should either be constant or random')
        self.request_timing_behaviour = new_timing_behaviour

    def set_user_agent_behaviour(self, new_ua_behaviour: int):
        """
        This function will determine after how many requests the user agent
        will be replaced for a new one.
        :param new_ua_behaviour: integer
        :return: None
        """
        if not isinstance(new_ua_behaviour, int):
            raise TypeError('The user agent behaviour should be of type integer')
        self.ua_behaviour = new_ua_behaviour
        logging.info('New user agent behaviour configured')

    def set_resource_dir(self, path: str):
        main_resource_dir = os.path.join('..', 'resources')
        specific_resource_dir = os.path.join(main_resource_dir, path)
        if not os.path.exists(specific_resource_dir):
            os.makedirs(specific_resource_dir)
            logging.info('New resource directory created')
        self.resource_path = specific_resource_dir

    def _check_max_pages(self) -> bool:
        """
        Function that check how many pages have been retrieved and compares that to
        the maximum allowed number of pages to crawl. Function is later used in self.crawl
        to stop the while loop.

        if max_pages_to_crawl is None, then no limit is assumed and the crawler will just keep going.
        :return:
        """
        if self.max_pages_to_crawl is None:
            return True
        return self.max_pages_to_crawl > self.requests_send_counter

    def _replace_user_agent(self):
        """
        Method that sets
        :return: True if a new user agent was set, False if the same was kept.
        """
        ua = UserAgent()
        if self.requests_send_counter % self.ua_behaviour == 0:
            self.user_agent = ua.random
            return True
        return False

    def _send_request(self, url):
        """
        Function to set up a tor connection and send a request under tor network.
        Cookie is chosen randomly from the list of COOKIES
        User agent is dependent on how many request have been sent by the crawler, see: self._replace_user_agent
        :param url: the url to download
        :return: response
        """
        self._replace_user_agent()
        if not self.cookies:
            header = {'User-Agent': self.user_agent}
        else:
            header = {'Cookie': random.choice(self.cookies), 'User-Agent': self.user_agent}
        web_page = requests.get(url, headers=header, proxies=self.proxies)
        self.requests_send_counter += 1
        return web_page

    def _detect_captcha(self, web_page) -> bool:
        """
        function that will scan the web page for a captcha
        :return: True if captcha is detected, false if not
        """
        pass

    def _extract_internal_links(self, web_page):

        request_url = web_page.request.url
        domain = urlparse(request_url).netloc

        # Make soup
        soup = BeautifulSoup(web_page.content, "html.parser", from_encoding="iso-8859-1")

        urls = set()

        # Get all internal links
        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            href = urljoin(request_url, href).strip("/")

            if href == "" or href is None:
                # href empty tag
                continue

            if urlparse(href).netloc != domain:
                # external link
                continue

            urls.add(href)

        return list(urls)

    def _save_resource(self, url, web_page):
        """
        function retrieved from lab session to save the crawled page to the resources repo
        :param url:
        :param web_page:
        :return:
        """
        filename = str(uuid.uuid4().hex) + ".html"
        path = os.path.join(self.resource_path, filename)
        with open(path, 'w') as file:
            file.write(web_page.text)
            logging.info(f"URL {url} saved under the name {filename}")
        return True

    def sync_resources(self):
        """
        method that synchronizes the resources that are kept in the local resources
        directory with the cloud bucket.
        :return:
        """
        pass

    def crawl(self):
        """
        This function is the runner function of the crawler
        :return: None
        """
        # error handling
        if not self.seed:
            raise ValueError('The SEED attribute must be set before crawling')

        if not self.resource_path:
            raise ValueError('The resource path must be inserted before crawling')

        # getting a SEED and adding it to the queue
        self.queue.append(self.seed)

        # start crawling until exit condition was reached
        while self.queue and self._check_max_pages():
            url = self.queue.popleft()

            if url not in self.visited:
                # Send tor request to download the page
                web_page = self._send_request(url)

                if self.request_timing_behaviour == 'constant':
                    time.sleep(self.request_interval)  # time between each request
                elif self.request_timing_behaviour == 'random':
                    time.sleep(random.randint(0, self.request_interval))

                # Update the visited pages
                self.visited.add(url)

                # Save the page into the download folder
                self._save_resource(url, web_page)

                # Extract all the internal links
                new_urls = self._extract_internal_links(web_page)
                for new_url in new_urls:
                    if new_url not in self.queue and new_url not in self.visited:
                        self.queue.append(new_url)