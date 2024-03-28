from fake_useragent import UserAgent
import requests
from requests.exceptions import Timeout
from bs4 import BeautifulSoup
from google.cloud import storage
from google.oauth2 import service_account

import os
import time
from datetime import datetime, timezone
import random
import logging
import sys
import pickle
from collections import deque
from urllib.parse import urlparse, urljoin
import json
import hashlib

import config.constants as c


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
        self.resource_path = str()  # give it the name of the marketplace we are scraping
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
        if not os.path.exists(main_resource_dir):
            os.mkdir(main_resource_dir)
        specific_resource_dir = os.path.join(main_resource_dir, path)
        if not os.path.exists(specific_resource_dir):
            os.makedirs(specific_resource_dir)
            logging.info('New resource directory created')
        self.resource_path = specific_resource_dir

    def _write_queue_to_file(self) -> bool:
        """
        Helper function which writes the current queue to a file when there were still items in the queue although
        the runner was not finished running.
        :return: True if queue written to file, else file
        """
        if self.queue:  # only write when there is data in deque
            marketplace_dir = os.path.basename(self.resource_path)
            deque_filename = '{}-queue.pkl'.format(marketplace_dir)
            with open(os.path.join(self.resource_path, deque_filename), 'wb') as f:  # overrides file if exists
                pickle.dump(self.queue, f)
            return True
        return False

    def _load_queue_from_file(self) -> bool:
        """
        Helper function that loads the queue from a file en sets it as a class variable when it exists.
        :return: True if queue was loaded from file else False
        """
        filename = '{}-queue.pkl'.format(os.path.basename(self.resource_path))
        location = os.path.join(self.resource_path, filename)
        if os.path.exists(location):
            with open(location, 'rb') as f:
                self.queue = pickle.load(f)
            return True
        return False

    def _check_max_pages(self) -> bool:
        """
        Function that check how many pages have been retrieved and compares that to
        the maximum allowed number of pages to crawl. Function is later used in self.crawl
        to stop the while loop.

        if max_pages_to_crawl is None, then no limit is assumed and the crawler will just keep going.
        :return: True if there is no maximum or when the limit has not been exceeded.
        """
        if self.max_pages_to_crawl is None:
            return True
        return self.max_pages_to_crawl > self.requests_send_counter

    def _replace_user_agent(self):
        """
        Method that replaces the current user agent for a random new one
        :return: True if a new user agent was set, False if the same was kept.
        """
        ua = UserAgent()
        if self.requests_send_counter % self.ua_behaviour == 0:
            self.user_agent = ua.random
            return True
        return False

    def _send_request(self, url) -> requests.Response:
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

    @staticmethod
    def _extract_internal_links(web_page: requests.Response) -> list:
        """
        Method that gets all the links on a html page, checks if they belong
        the domain we are scraping, then returns them as a list.
        """
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

    @staticmethod
    def _hash_url(url: str) -> str:
        """
        Method that will be used to hash the urls, so that they can later be used to store the urls.
        Algorithm used is MD5
        :param url: The url to be hashed
        :return: The hashed url
        """
        # Create an MD5 hash object
        hash_obj = hashlib.md5()

        # Update the hash object with the input string, encoded to bytes
        hash_obj.update(url.encode())

        # Return the hexadecimal digest of the hash
        return hash_obj.hexdigest()

    def _save_resource(self, url: str, web_page: requests.Response) -> bool:
        """
        function retrieved from lab session to save the crawled page to the resources repo
        :param url:
        :param web_page:
        :return: True if resource saved, else error
        """
        hashed_url = self._hash_url(url)
        filename = hashed_url + ".html"

        path = os.path.join(self.resource_path, filename)
        with open(path, 'w') as file:
            file.write(web_page.text)
            logging.info(f"URL {url} saved under the name {filename}")
            return True

    @staticmethod
    def _get_bucket() -> storage.Bucket:
        """
        helper that configures a bucket
        :return: configured bucket
        """
        credentials = service_account.Credentials.from_service_account_file(
            c.GOOGLE_APPLICATION_CREDENTIALS
        )
        storage_client = storage.Client(credentials=credentials)
        return storage_client.bucket(bucket_name=c.BUCKET_NAME)  # returns bucket object

    def upload_resources(self):
        """
        method that uploads resources that are kept in the local resources
        directory to the cloud bucket. Also uploads files that have been changed more recently locally. Only uploads
        and does not download from bucket.
        :return: None
        """
        bucket = self._get_bucket()
        # looping over local resource directory
        resources_directory = os.path.dirname(self.resource_path)
        for root, dirs, files in os.walk(resources_directory):
            for filename in files:
                if filename in {'.DS_Store'}:
                    continue
                local_file = os.path.join(root, filename)

                relative_path = os.path.relpath(local_file, resources_directory)
                blob = bucket.get_blob(relative_path)

                # Compare last modification times or other logic for syncing
                if not blob.exists() or os.path.getmtime(local_file) > datetime.timestamp(
                        blob.updated.replace(tzinfo=timezone.utc)):
                    # Upload the file if it doesn't exist or if the local version is newer
                    blob.upload_from_filename(local_file)
                    print(f"Uploaded {local_file} to {relative_path} in bucket {c.BUCKET_NAME}")

    def download_resources(self):
        """
        Method that downloads resources from the cloud bucket that are not in the local directory.
        """
        pass

    def crawl(self):
        """
        This method is used to neatly set up invoke the main functionality of the class: 🕸🕷️️ CRAWLING 🕷️🕸️
        :return: None
        """

        def _write_json_file(file_location, file_data):
            """
            overwriting existing file with the new data
            :param file_location:
            :param file_data:
            :return:
            """
            with open(file_location, 'w') as f:
                json.dump(file_data, f)

        # error handling
        if not self.seed:
            raise ValueError('The SEED attribute must be set before crawling')

        if not self.resource_path:
            raise ValueError('The resource path must be inserted before crawling')

        # setting up file path for the file where the network data is stored
        json_file_name = os.path.basename(self.resource_path) + '.json'
        json_file_loc = os.path.join(self.resource_path, json_file_name)

        # opening existing file or creating new one if not exists
        if os.path.exists(json_file_loc):
            with open(json_file_loc, 'r') as jf:
                json_file = json.load(jf)
        else:
            # if the file does not exist jet, we start with an empty dictionairy
            json_file = dict()

        if not self._load_queue_from_file():
            # getting a SEED and adding it to the queue when queue was not loaded from file
            self.queue.append(self.seed)

        try:
            # start crawling until exit condition was reached
            while self.queue and self._check_max_pages():
                url = self.queue.popleft()
                hashed_url = self._hash_url(url)  # required later for logging

                # url can not be in current crawling session and not in previous crawls
                if (url not in self.visited) and (hashed_url not in json_file.keys()):
                    # Send tor request to download the page
                    web_page = self._send_request(url)

                    # insert some waiting time in between each request
                    if self.request_timing_behaviour == 'constant':
                        time.sleep(self.request_interval)  # time between each request
                    elif self.request_timing_behaviour == 'random':
                        time.sleep(random.randint(0, self.request_interval))

                    # Update the visited pages
                    self.visited.add(url)

                    # Extract all the internal links
                    new_urls = self._extract_internal_links(web_page)

                    # hash the urls for logging
                    url_object = {hashed_url: {"original": url}}  # storing the original url as its value
                    url_children = {self._hash_url(n_url): n_url for n_url in new_urls}  # the same for internal links
                    url_object[hashed_url].update({"children": url_children})  # adding its children to the object
                    # now the original and the children can easily be referenced with:
                    # url_object[hashed_url].get("original") OR url_object[hashed_url].get("children")

                    # checking if the url is not already in the data
                    if self._hash_url(url) not in json_file.keys():
                        json_file.update(url_object)  # updating the current json file in memory
                        if sys.getsizeof(json_file) > (10 * 1024 * 1024):
                            _write_json_file(file_location=json_file_loc, file_data=json_file)  # writing if > 10 MB

                    # Save the page into the resource folder
                    self._save_resource(url, web_page)

                    # adding only the urls that are not in queue already and not in visited
                    # Note: we are collecting data about all urls in the step above, which will allow us to
                    #       visualize the whole structure of the marketplace
                    for new_url in new_urls:
                        if new_url not in self.queue and new_url not in self.visited:
                            self.queue.append(new_url)
                else:
                    logging.info('URL: {} has already been scraped!'.format(url))

        except (KeyboardInterrupt, Timeout):  # writing when interrupted or request taking too long
            _write_json_file(file_location=json_file_loc, file_data=json_file)
            if self._write_queue_to_file():
                logging.info('Interrupted and queue written to file')

        else:
            _write_json_file(file_location=json_file_loc, file_data=json_file)  # writing when everything went fine
            if self._write_queue_to_file():
                logging.info('Process finished and queue written to file')
