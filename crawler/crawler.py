import bs4
from fake_useragent import UserAgent
import requests
from requests.exceptions import Timeout
from bs4 import BeautifulSoup

import os
import time
from datetime import datetime
import random
import logging
import sys
import pickle
import subprocess
from collections import deque
from urllib.parse import urlparse, urljoin
import json
import hashlib

import config.constants as c
from crawler.captcha.detector import CaptchaDetector


class Crawler:
    """
    Crawler class is used to crawl pages on the darkweb.
    ...
    Attributes
    ----------

    ...
    Methods
    ----------

    """

    logging.basicConfig(level=logging.INFO, stream=sys.stdout, )

    def __init__(self):
        self.cookies = list()
        self.seed = str()
        self.proxies = {'http': 'socks5h://localhost:9050',
                        'https': 'socks5h://localhost:9050'}
        self.max_pages_to_crawl = None
        self.request_waiting_time = None  # the time between each request
        self.ua_behaviour = 1
        self.user_agent = None
        self.visited = set()
        self.queue = deque()
        self.requests_send_counter = int()
        self.marketplace_name = str()  # name of the marketplace
        self.resource_path = str()  # the marketplace directory from the repo root
        self.seed = str()
        self.exit_condition = bool()
        self.captcha_detector = CaptchaDetector()
        self.synchronize = True

    def set_cookies(self, cookies: list):
        """Method that sets the cookies that will be used for sending requests. A cookie can be obtained by creating a
        account on a dark web marketplace, inspecting the send request with tor and copying the cookie.
        :param cookies: a list of strings"""
        if not isinstance(cookies, list):
            raise TypeError('Cookies should be inserted as list')
        else:
            self.cookies = cookies

    def set_seed(self, url: str):
        """Method that sets the union address of the first request. If a queue already exists for marketplace, then
        this method is not required.
        :param url: string that ends with .onion
        """
        if not isinstance(url, str):
            raise TypeError('url should be of type string')
        if 'onion' not in url:
            raise ValueError('url should be an union url')

        self.seed = url

    def set_max_pages_to_crawl(self, max_pages: int):
        """Method that will terminate the crawler when the maximum number of pages crawled in one session has been
        reached.
        :param max_pages: an integer representing the maximum number of pages to crawl in a session."""
        if not isinstance(max_pages, int):
            raise TypeError('Condition is not of type bool')
        else:
            self.max_pages_to_crawl = max_pages

    def set_request_timing(self, waiting_time: int | tuple):
        # Validate that the input is either an integer or a tuple
        if not isinstance(waiting_time, (int, tuple)):
            raise TypeError('Time should be either an integer or a tuple of two integers')

        # Handle the cases based on input type
        if isinstance(waiting_time, int):
            # Ensure the integer is non-negative
            if waiting_time < 0:
                raise ValueError('Time interval as integer should be non-negative')
            self.request_waiting_time = waiting_time
        elif isinstance(waiting_time, tuple):
            # Ensure the tuple contains exactly two integers
            if len(waiting_time) != 2:
                raise ValueError('Time tuple should contain exactly two integers')
            lower, upper = waiting_time

            # Ensure both elements are integers
            if not isinstance(lower, int) or not isinstance(upper, int):
                raise TypeError('Both elements of the tuple must be integers')

            # Ensure the upper bound is greater than the lower bound
            if upper <= lower:
                raise ValueError('Upper bound should be greater than lower bound')

            self.request_waiting_time = (lower, upper)

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

    def set_resource_dir(self, marketplace_name: str):
        self.marketplace_name = marketplace_name
        main_resource_dir = os.path.join('resources')
        if not os.path.exists(main_resource_dir):
            os.mkdir(main_resource_dir)
        specific_resource_dir = os.path.join(main_resource_dir, self.marketplace_name)
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
        if self.queue:  # only write when there is data in queue
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
            logging.info('Loaded queue from file')
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

    def _send_request(self, url) -> (requests.Response, dict):
        """
        Function to set up a tor connection and send a request under tor network.
        Cookie is chosen randomly from the list of COOKIES
        User agent is dependent on how many request have been sent by the crawler, see: self._replace_user_agent
        :param url: the url to download
        :return: response
        """

        def _check_for_queue(web_page: requests.Response) -> bool:
            waiting_cue_words = ['waiting', 'checking your browser before accessing nexus market']
            web_page_soup = bs4.BeautifulSoup(web_page.text, features="html.parser").text.lower()
            for word in waiting_cue_words:
                if word in web_page_soup:
                    return True
            return False

        self._replace_user_agent()
        if not self.cookies:
            header = {'User-Agent': self.user_agent}
        else:
            header = {'Cookie': random.choice(self.cookies), 'User-Agent': self.user_agent}
        web_page = requests.get(url, headers=header, proxies=self.proxies)

        # if queue detected: change cookies
        # if _check_for_queue(web_page):
        #     logging.info('Crawler in queue, waiting 30 seconds')
        #     cookie = web_page.headers.get('Set-Cookie')
        #     time.sleep(30)
        #     new_header = {'Cookie': cookie, 'User-Agent': self.user_agent}
        #     web_page = requests.get(url, headers=new_header, proxies=self.proxies)

        self.requests_send_counter += 1
        return web_page, header.get('Cookie', None)

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

    def synchronize_resources(self) -> None:
        """
        Method used to synchronize all files in '../resources' with a cloud bucket. If a file must be deleted for
        some reason use self.delete_resource.
        """
        if self.synchronize:
            logging.info('Started synchronizing resources')
            command = 'gsutil -m rsync -r resources gs://{}'.format(c.BUCKET_NAME)
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Check the result
            if result.returncode == 0:
                logging.info('Synchronized resources')
            else:
                logging.info('Error synchronizing resources:\t{}'.format(result.stderr))

    def crawl(self):
        """
        This method is used to neatly set up invoke the main functionality of the class: 🕸🕷️️ CRAWLING 🕷️🕸️
        To start crawling, a few ingredients are required:
        - The location where the crawled resources should be kept. In this directory the following three items will be
        stored: the HTML pages, the queue.pkl file and network information data in json format.
        - A seed. An exception exists in the case that there already is a queue stored in a file. If that is the case,
        seed does not have to be set.
        :return: None
        """

        def _write_network_data(file_location, file_data):
            """
            overwriting existing file with the new data
            :param file_location:
            :param file_data:
            :return:
            """
            with open(file_location, 'w') as f:
                json.dump(file_data, f)

        # error handling
        if not self.resource_path:
            raise ValueError('The resource directory name must be inserted before crawling')

        # setting up file marketplace_dir for the file where the network data is stored
        network_data_filename = os.path.basename(self.resource_path) + '.json'
        network_data_file_loc = os.path.join(self.resource_path, network_data_filename)

        # opening existing network file or creating new one if not exists
        if os.path.exists(network_data_file_loc):
            with open(network_data_file_loc, 'r') as jf:
                network_data = json.load(jf)
                logging.info('Loaded network data from existing file')
        else:
            # if the file does not exist jet, we start with an empty dictionary
            network_data = dict()

        # getting a seed and adding it to the queue if the queue was not loaded from file
        if not self._load_queue_from_file():

            if not self.seed:
                raise ValueError(
                    'The seed attribute must be set before crawling or an existing crawler queue must exist'
                )

            self.queue.append(self.seed)

        try:
            # start crawling until exit condition was reached
            while self.queue and self._check_max_pages():
                url = self.queue.popleft()
                hashed_url = self._hash_url(url)  # later needed for logging network information

                # url can not be in current crawling session and not in previous crawls
                if (url not in self.visited) and (hashed_url not in network_data.keys()):
                    # Send tor request to download the page
                    web_page, used_cookie = self._send_request(url)
                else:
                    logging.info("Url: {} already visited".format(url))
                    continue

                # Check if the page is a captcha
                if self.captcha_detector.detect_captcha(web_page.text):
                    logging.info('Captcha Detected ')
                    # save file to captcha training data
                    new_captcha_page = datetime.now().strftime('%H:%M:%S %d-%m-%Y') + ' ' + \
                                       self.marketplace_name + '.html'
                    captcha_page_location = os.path.join('crawler', 'captcha', 'training-data',
                                                         'detected', new_captcha_page)

                    with open(captcha_page_location, 'w') as cp:
                        cp.write(web_page.text)

                    time.sleep(32)

                    # # Delete the cookie if the crawler has cookies
                    # if self.cookies:
                    #     self.cookies.remove(used_cookie)
                    #     logging.info('Removed cookie from list')
                    #
                    # # raise error message when no more cookies left
                    # if not self.cookies:
                    #     raise CaptchaDetectedError('The Crawler detected a page with captcha and stopped crawling')

                else:
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
                    if self._hash_url(url) not in network_data.keys():
                        network_data.update(url_object)  # updating the current json file in memory
                        # writing network data to file if > 10 MB
                        if sys.getsizeof(network_data) > (10 * 1024 * 1024):
                            _write_network_data(file_location=network_data_file_loc, file_data=network_data)

                    # Save the page into the resource folder
                    self._save_resource(url, web_page)

                    # adding only the urls that are not in queue already and not in visited
                    # Note: we are collecting data about all urls in the step above, which will allow us to
                    #       visualize the whole structure of the marketplace
                    for new_url in new_urls:
                        if new_url not in self.queue and new_url not in self.visited:
                            self.queue.append(new_url)
                        else:
                            logging.debug('URL: {} has already been scraped!'.format(url))

                    # insert some waiting time in between each request
                    if isinstance(self.request_waiting_time, int):
                        time.sleep(self.request_waiting_time)  # time between each request
                    elif isinstance(self.request_waiting_time, tuple):
                        lower, upper = self.request_waiting_time
                        time.sleep(random.randint(lower, upper))

            else:
                _write_network_data(file_location=network_data_file_loc,
                                    file_data=network_data)  # writing when everything went fine
                self._write_queue_to_file()
                logging.info('Process finished and queue written to file')
                self.synchronize_resources()

        except CaptchaDetectedError:
            _write_network_data(file_location=network_data_file_loc, file_data=network_data)
            self._write_queue_to_file()
            self.synchronize_resources()
            logging.info('Captcha detected')

        except Timeout:
            _write_network_data(file_location=network_data_file_loc, file_data=network_data)
            self._write_queue_to_file()
            self.synchronize_resources()
            logging.info('Request timed out')

        except KeyboardInterrupt:
            _write_network_data(file_location=network_data_file_loc, file_data=network_data)
            self._write_queue_to_file()
            self.synchronize_resources()
            logging.info('Crawler manually interrupted')

        except Exception as e:  # just any error
            print(f'An error occurred with {e}')
            _write_network_data(file_location=network_data_file_loc, file_data=network_data)
            self._write_queue_to_file()
            self.synchronize_resources()
            logging.info('Interrupted and queue written to file')


class CaptchaDetectedError(Exception):
    def __init__(self, message):
        super().__init__(message)
