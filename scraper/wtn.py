import logging
import re

from bs4 import BeautifulSoup
from generic import GenericScraper


class WeTheNorthScraper(GenericScraper):
    def __init__(self, marketplace_dir):
        super().__init__(marketplace_dir)

    def check_if_valid(self, page: BeautifulSoup) -> bool:
        return True

    def detect_page_type(self, page: BeautifulSoup):
        detected_types = set()

        if page.find(id='desc_prod'):
            for x in ['product', 'review']:
                detected_types.add(x)

        elif 'Vendor Profile' in page.text:
            detected_types.add('vendor')

        return detected_types

    def scrape_page_and_write_data(self, page_type, page, filepath):

        data = {'vendor': None, 'product': None, 'review': None}

        if 'vendor' in page_type:
            data['vendor'] = self.scrape_vendor(page)

        if 'product' in page_type:
            data['product'] = self.scrape_product(page)

        if 'review' in page_type:
            vendor_name = data['product'][-2]
            data['review'] = self.scrape_review(page, vendor_name)

        if not data.values():
            logging.info(f'No data scraped on page: {filepath}')
            return

        for key, value in data.items():
            if value:
                self.write_to_csv(table=key, data=value)
                logging.info(f'Wrote data to {key}')

        self.log_done(filepath)

    def scrape_product(self, page):
        tabcontent = page.find('div', class_='tabcontent')

        if tabcontent:
            product_name = tabcontent.find('h3')
            if product_name:
                product_name = product_name.text.strip()
        else:
            product_name = ''

        if not product_name:
            p_name2 = page.find('h2', style='margin:0px;')
            if p_name2:
                product_name = p_name2.text.strip()

        bigimage_div = page.find('div', class_='bigimage')
        if bigimage_div:
            product_img = bigimage_div.find('img')
            if product_img:
                product_picture = product_img.get('src')
            else:
                product_picture = ''
        else:
            product_picture = ''

        count_and_since = page.find(string=re.compile(r'sold since'))
        if count_and_since:
            count, since = count_and_since.text.split('sold since')
        else:
            count, since = '', ''

        cur_and_price_tag = page.find('p', class_='padp', style='margin-bottom: 10px;')
        if cur_and_price_tag:
            curr_and_price = cur_and_price_tag.find('span')
            if curr_and_price:
                curr, price = curr_and_price.text.split('$')
            else:
                curr, price = '', ''
        else:
            curr, price = '', ''

        desc = page.find('p', style='word-wrap: break-word; white-space: pre-wrap;')
        if desc:
            desc = desc.text.strip()
        else:
            desc = ''

        pclass_ship_origin = list()
        for field in ['Product Class', 'Ships to', 'Origin Country']:
            word = page.find('td', string=field)
            if word:
                value = word.find_next_sibling()
                if value:
                    value = value.text.strip()
                    pclass_ship_origin.append(value)

        if len(pclass_ship_origin) == 3:
            product_category, ship_from, ship_to = pclass_ship_origin
        else:
            product_category, ship_from, ship_to = '', '', ''

        # vendorname
        vendor_tag = page.find(string=re.compile(r'Sold by'))
        if vendor_tag:
            vendor_name = vendor_tag.find_next('a').text
        else:
            vendor_name = ''

        return [
            product_name,
            product_category,
            product_picture,
            since,
            count,
            price,
            curr,
            desc,
            ship_from,
            ship_to,
            vendor_name,
            'WeTheNorth'
        ]

    def scrape_vendor(self, page):

        # vendor name
        head_tag = page.find('h3', class_='user_info_mid_head')
        if head_tag:
            vendor_name = head_tag.text.split(' ')[0]
        else:
            vendor_name = ''

        # about text
        about_element = page.find('h3', string='About')
        if about_element:
            about_text = about_element.find_next()
            if about_text:
                about_text = about_text.text.strip()
        else:
            about_text = ''

        # profile picture
        profile_picture = ''
        user_info = page.find('div', class_='user_info')
        if user_info:
            img_tag = user_info.find('img')
            if img_tag:
                profile_picture = img_tag.get('src', '')

        # pgp_key
        pgp_key = ''
        pgp_element = page.find('h3', string='PGP')
        if pgp_element:
            pgp_tag = pgp_element.find_next_sibling()
            if pgp_tag:
                pgp_key = pgp_tag.text.strip()

        # wallet address
        wallet_address = ''

        word_tag = page.find('p', class_='boldstats')
        print(word_tag)
        if word_tag:
            review_count = word_tag.text.strip().split(' ')
            for item in review_count:
                if item.isdigit():
                    review_count = item
                    break
        else:
            review_count = ''

        rating = ''

        sale_count = ''

        historic_sale_count = ''

        marketplace = 'WeTheNorth'

        marketplace_history = ''

        return [
            vendor_name,
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

    def scrape_review(self, page, vendor_name):
        reviews_counter = 0
        total_feedback_element = page.find('p', class_='boldstats')
        if total_feedback_element:
            for char in total_feedback_element.text.strip():
                if char.isdigit():
                    reviews_counter += int(char)
            if reviews_counter == 0:
                total_feedback_element.text.strip()
                return []
        else:
            return []

        # vendor name
        gen_desc_element = page.find('p', id='desc_prod')
        if gen_desc_element:
            vendor_element = gen_desc_element.find_next('a')
            if vendor_element:
                vendor_name = vendor_element.text.strip()
            else:
                vendor_name = ''
        else:
            vendor_name = vendor_name

        product_element = page.find('div', class_='listDes')
        if product_element:
            product_name = product_element.find_next('h2').text.strip()
        else:
            product_name = ''

        description_element = page.find('a', string='Description')
        if description_element:
            product_link = ('http://hn2paw7zaahbikbejiv6h22zwtijlam65y2c77xj2ypbilm2xs4bnbid.onion/' +
                            description_element.get('href'))
        else:
            product_link = ''

        feedback_list = []
        feedback_table = page.find('table', class_="user_feedbackTbl autoshop_table")
        if feedback_table:
            rows = feedback_table.find_all('tr')
            if rows:
                rows.pop(0)
            for tr in feedback_table.find_all('tr'):
                # find the product_link, datetime, author, rating, text, price_paid and currency
                # find text, rating, author, price, curr, author

                feedback_img = tr.find('img')
                if feedback_img:
                    if feedback_img.get('src') == 'files/feedback1.png':
                        rating = 'positive'
                    else:
                        rating = 'negative'
                else:
                    rating = ''

                row_p_tags = tr.find_all('p')
                if row_p_tags:

                    text, product, author_cur_price, date = row_p_tags
                    author, cur, price = author_cur_price.text.split()

                    feedback_list.append(
                        [
                            vendor_name,
                            product_name,
                            product_link,
                            date.text.strip(),
                            author,
                            rating,
                            text.text.strip(),
                            price,
                            cur
                        ]
                    )

                else:
                    continue

        return feedback_list


if __name__ == "__main__":
    wtn_scraper = WeTheNorthScraper(marketplace_dir='we-the-north')
    wtn_scraper.start()
