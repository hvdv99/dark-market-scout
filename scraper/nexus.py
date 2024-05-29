import re
import logging

from bs4 import BeautifulSoup
from generic import GenericScraper


class NexusScraper(GenericScraper):
    def __init__(self, marketplace_dir):
        super().__init__(marketplace_dir)

    def check_if_valid(self, page: BeautifulSoup) -> bool:
        """Method that checks if a page is valid to scrape based on marketplace specific rules"""

        if 'Sorry, the page you are looking for could not be found.' in page.text:
            return False

        return True

    def scrape_page_and_write_data(self, page_type, page, filepath):
        data = {'vendor': None, 'product': None, 'review': None}

        if 'vendor' in page_type:
            data['vendor'] = self.scrape_vendor(page)

        if 'review' in page_type:
            vendor_name = data['vendor'][0]
            data['review'] = self.scrape_review(page, vendor_name)

        if 'product' in page_type:
            data['product'] = self.scrape_product(page)

        for key, value in data.items():
            if value:
                self.write_to_csv(table=key, data=value)
            logging.info(f'Wrote data to {key}')

        self.log_done(filepath)

    def detect_page_type(self, page: BeautifulSoup):
        detected_types = set()
        if 'Add to Cart' in page.text:
            detected_types.add('product')

        elif 'Public key' in page.text:
            for x in ['vendor', 'review']:
                detected_types.add(x)
        return detected_types

    def scrape_product(self, soup):
        # Product name
        scraped_name = soup.find('h1', class_="text-2xl").text
        name = scraped_name.strip() if scraped_name else ''

        category_tags = soup.find_all('a', class_='hover:text-base-500 duration-[750ms]')
        if len(category_tags) > 0:
            category = ''
            for ct in category_tags:
                category += ct.text.strip() + ' '
        else:
            category = ""

        # Product picture
        picture = soup.find('a', class_='image-box')['href'] if soup.find('a',
                                                                          class_='image-box') else ""

        # Sold since (Not directly available, setting a default)
        sold_since = "not-on-nexus"

        # Sold count
        sold_count = "not-on-nexus"

        # Price and currency
        cur_and_price = soup.find('dd', class_="order-first text-sm font-semibold tracking-tight text-green-500")
        scraped_currency = cur_and_price.find('span').extract().text.strip()
        currency = scraped_currency if scraped_currency else ''
        scraped_price = cur_and_price.text.strip()
        price = scraped_price if scraped_price else ''

        # Description
        description = soup.find('div', id="description-data").findChild('p').text.strip() if soup.find(
            'div', id="description-data").findChild('p') else ''

        # Shipped from (Not directly available, setting a default)
        shipped_from = 'not-on-nexus'

        # Shipped to (Not directly available, setting a default)
        shipped_to = 'not-on-nexus'

        # Vendor
        vendor = soup.find('h1', class_='font-semibold text-center text-xl text-lime-500').text.strip() if soup.find(
            'h1', class_='text-2xl') else "Not Available"

        # Marketplace
        marketplace = "nexus"

        return [
            name,
            category,
            picture,
            sold_since,
            sold_count,
            price,
            currency,
            description,
            shipped_from,
            shipped_to,
            vendor,
            marketplace
        ]

    def scrape_vendor(self, page):

        def extract_numbers_as_integer(input_string):

            # Extract all numbers using regular expression
            numbers = re.findall(r'\d+', input_string)

            # Concatenate the numbers
            concatenated_numbers = ''.join(numbers)

            # Convert to integer, or return 0 if no numbers were found
            return int(concatenated_numbers) if concatenated_numbers else 0

        name = page.find('h2', class_="text-lg").text

        about_div = page.find('div', id='about-data')
        if about_div:
            about_text = about_div.find('p').extract().text
        else:
            about_text = 'Not found'

        profile_picture = 'NA'

        code_tags = page.find_all('code')
        if len(code_tags) == 2:
            pgp_key = code_tags[1].text
        else:
            pgp_key = ''

        wallet_address = 'NA'

        sales_word_tag = page.find(lambda tag: tag.string and 'Sales' in tag.string)
        next_sibling_sales = sales_word_tag.find_next_sibling() if sales_word_tag else None
        sale_count = next_sibling_sales.text if next_sibling_sales else None

        historic_sales_word_tag = page.find(lambda tag: tag.string and 'Historical Sales' in tag.string)
        if historic_sales_word_tag:
            next_sibling_historic_sales = (historic_sales_word_tag.find_next_sibling()
                                           if historic_sales_word_tag
                                           else None)
            historic_sale_count = next_sibling_historic_sales.text if next_sibling_sales else None
        else:
            historic_sale_count = 0

        rating_tag = page.find('div', class_='text-xs text-gray-400/80 hover:text-gray-400 font-semibold')
        if rating_tag:
            max_rating = rating_tag.find('span').extract()
            rating = float(rating_tag.text) / extract_numbers_as_integer(max_rating.text)
        else:
            rating = ''

        review_word_tag = page.find(lambda tag: tag.string and 'Reviews' in tag.string)
        next_sibling_review = review_word_tag.find_next_sibling() if review_word_tag else None
        review_count = next_sibling_review.text.strip() if next_sibling_review else None

        marketplace = 'nexus'

        marketplace_history = {}
        other_market_history = page.find_all('div', class_='px-4 text-gray-700')
        if other_market_history:
            for element in other_market_history:
                marketplace_name = element.find('h3').text.strip()
                span_tags = element.find_all('span')
                if len(span_tags) == 2:
                    h_sales, h_rating = span_tags
                    marketplace_history[marketplace_name] = {'sales': h_sales.text.strip(),
                                                             'rating': h_rating.text.strip()}

        return [
            name,
            about_text,
            profile_picture,
            pgp_key,
            wallet_address,
            review_count,
            rating,
            sale_count,
            historic_sale_count,
            marketplace,
            marketplace_history
        ]

    def scrape_review(self, soup, vendor):

        review_element = soup.find('div', id='reviews-data')
        if review_element:
            review_data = review_element.find_all('div', class_="p-4 flex flex-col h-full") if review_element.find_all(
                'div', class_="p-4 flex flex-col h-full") else []
        else:
            return []

        reviews = []
        for element in review_data:
            all_spans = element.find_all('span')
            all_p = element.find_all('p')

            # Extracting date from the first span with text
            when = all_spans[0].text.strip()

            # Extracting product link and name
            a_tag = element.find('a')
            if a_tag:
                prod_link = a_tag.get('href')
                prod_name = a_tag.text.strip()
            else:
                prod_link = ''
                prod_name = ''

            # Extracting rating and review text
            rating = all_p[0].text.strip() if all_p else ''
            review_text = all_p[1].text.strip() if len(all_p) > 1 else ''

            # Extracting price and currency from the last span element containing the price
            price_info = all_spans[-1].text.strip()
            if price_info:
                parts = price_info.split()
                price = parts[0]
                currency = parts[1] if len(parts) > 1 else ''
            else:
                price = ''
                currency = ''

            author = 'nexus-no-author'
            a_review = [
                vendor,
                prod_name,
                prod_link,
                when,
                author,
                rating,
                review_text,
                price,
                currency
            ]
            reviews.append(a_review)
        return reviews


if __name__ == "__main__":
    nexus = NexusScraper('nexus')
    nexus.start()
