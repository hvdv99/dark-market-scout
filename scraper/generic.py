import os
import json
import csv
import sys
import random
import logging
from pathlib import Path
from abc import ABC, abstractmethod

import bs4
from bs4 import BeautifulSoup

from crawler.crawler import Crawler


class GenericScraper(ABC):

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    def __init__(self, marketplace_dir):
        self.marketplace_dir = marketplace_dir
        self.data_location = os.path.join('..', 'resources', marketplace_dir)
        self.filenames = [os.path.join(self.data_location, f) for f in os.listdir(self.data_location)
                          if f.endswith('.html')]
        self.logdir = 'logs'
        self.logfile = f'scraping-logs-{marketplace_dir}.txt'
        self.logfile_error = f'scraping-error-logs-{marketplace_dir}.txt'

        self.scraped_data_dir = 'scraped'

        self.network_file = self.load_network_file()
        self.hash_func = Crawler(train_captcha_detector=False).hash_url

    def load_network_file(self):
        with open(os.path.join(self.data_location, f'{self.marketplace_dir}.json')) as f:
            return json.load(f)

    def get_original_url(self, path):
        hashed_filename = os.path.basename(path)
        hashed_url = Path(hashed_filename).stem
        network_object = self.network_file.get(hashed_url)

        if network_object:
            original_url = network_object.get('original')
            return original_url
        else:
            # No original URL saved
            return

    def load_page(self) -> tuple:
        """reads a html file from the list of scraped files and returns it as a Beautifulsoup object."""

        random.shuffle(self.filenames)

        while self.filenames:
            path = self.filenames.pop()

            original_url = self.get_original_url(path)
            if not original_url:
                self.log_error(message='No Original URL', filepath=path)
                original_url = 'url-not-saved'

            with open(path, 'r') as f:
                try:
                    page = BeautifulSoup(f.read(), "html.parser", from_encoding="iso-8859-1")
                    if self.check_if_valid(page=page):
                        return page, original_url, path
                    else:
                        self.log_error(message='Page Not Valid For Scraping', filepath=path)

                except UnicodeDecodeError as e:
                    self.log_error(message='UnicodeDecodeError', filepath=path)
                    logging.error(f'Decoding error in file {path}: {e}')

                except FileNotFoundError as e:
                    self.log_error(message='FileNotFoundError', filepath=path)
                    logging.error(f'File not found {path}: {e}')

                except Exception as e:
                    self.log_error(message=e, filepath=path)
                    logging.error(f'An unexpected error occurred with file {path}: {e}')

    def log_done(self, filepath):
        """logs the filepath to the log file"""
        with open(os.path.join(self.logdir, self.logfile), 'a') as log_file:
            log_file.write(f'{filepath}\n')

    def log_error(self, message, filepath):
        """logs the filepath to the log file"""
        with open(os.path.join(self.logdir, self.logfile_error), 'a') as log_file:
            log_file.write(f'{message}:\t{filepath}\n')

    def write_to_csv(self, table, data):
        """
        Method that will write data to the appropriate csv table, creating the file with headers if it doesn't exist.
        """

        # Define CSV file path
        csv_filename = self.marketplace_dir + '-' + table
        csv_filepath = os.path.join(self.scraped_data_dir, f'{csv_filename}.csv')

        # Define headers for each table
        headers = {
            'review': ['vendor', 'product', 'product_link', 'datetime', 'author', 'rating', 'text', 'price_paid',
                       'currency'],
            'product': ['name', 'category', 'picture', 'sold_since', 'sold_count', 'price', 'currency', 'description',
                        'shipped_from', 'shipped_to', 'vendor', 'marketplace'],
            'vendor': ['name', 'about_text', 'profile_picture', 'pgp_key', 'wallet_address', 'review_count', 'rating',
                       'sale_count', 'historic_sale_count', 'marketplace', 'marketplace_history']
        }

        # Check if the CSV file exists
        file_exists = os.path.exists(csv_filepath)

        # Open the file in append mode and create it if it doesn't exist
        with open(csv_filepath, 'a', newline='') as file:
            writer = csv.writer(file)

            # If the file doesn't exist, write the header
            if not file_exists:
                writer.writerow(headers[table])

            # Write data
            if isinstance(data[0], list):  # Check if 'data' is a list of lists
                writer.writerows(data)
            else:
                writer.writerow(data)

    def start(self):

        page, original_url, filepath = self.load_page()

        while page:

            page_types = self.detect_page_type(page)

            try:
                self.scrape_page_and_write_data(page_types, page, filepath)

            except Exception as e:
                logging.info(f'The following error occurred: {e}\nWith page types: {page_types}')
                self.log_error(message=f'Unkown Error -> {e}', filepath=filepath)
                break  # The scraper must stop if we can not determine the source of error

            page_info = self.load_page()
            if page_info:
                page, original_url, filepath = page_info
            else:
                page = None

        else:
            logging.info('Scraping done')

    @abstractmethod
    def check_if_valid(self, page: BeautifulSoup) -> bool:
        """Method that checks if a page is valid to scrape based on marketplace specific rules"""
        pass

    @abstractmethod
    def detect_page_type(self, page: bs4.BeautifulSoup) -> set:
        """Detects what content type can be found on a page"""
        pass

    @abstractmethod
    def scrape_product(self, page) -> list:
        pass

    @abstractmethod
    def scrape_vendor(self, page) -> list:
        pass

    @abstractmethod
    def scrape_review(self, page, vendor_name) -> list:
        pass

    @abstractmethod
    def scrape_page_and_write_data(self, page_type, page, filepath):
        """Method required to be abstract since the scraping order is different for each marketplace."""
        pass
