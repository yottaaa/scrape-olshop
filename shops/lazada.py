from requests_html import HTML
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os
import pandas as pd

class LazadaScrape:

    def __init__(self, keyword):
        self.keyword = keyword
        self.shop = 'lazada'
        self.base_url = 'https://www.lazada.com.ph'
        chrome_options = Options()

        chrome_options.add_argument('disable-notifications')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('start-maximized')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=0")

        self.browser = webdriver.Chrome(
			executable_path=os.environ['CHROME_WEBDRIVER'],
			options=chrome_options
		)
        self.browser.get(self.base_url)

        self.search_el = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, 'q'))
        )
        self.search_el.send_keys(self.keyword)
        self.search_el.send_keys(Keys.RETURN)
        print(f'Searching for "{self.keyword}" on {self.base_url}')
        
        self.result = list()

    def convert_to_int(self,str_) -> int:
        to_num = str_.split()[0]
        num = 0
        if to_num.isalpha() != True:
            num = to_num
        return num

    # convert ratings count to int
    def convert_ratings_count_int(self, ratings_count) -> int:
        try:
            remove_str = {'ratings':'','Ratings':'','.':'','K':'00'}
            
            for k,v in remove_str.items():
                ratings_count = ratings_count.replace(k,v)
                
            return int(ratings_count)
        except ValueError:
            return 0
		
        return 0

    def convert_to_csv(self):
		# convert search result to csv file
        products_df = pd.DataFrame.from_dict(self.result)
        products_df.to_csv(
			f'{self.shop}_search_{"_".join(self.keyword.split("+"))}.csv', 
			index=False, 
			header=True
		)

    def search_result(self):
        product_img = ''
        product_link = ''
        product_name = ''
        product_price = ''
        product_ratings_avg = 0.0
        product_ratings_count = 0
        product_price_currency = ''

        # get products
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-qa-locator="general-products"]'))
        )
        sleep(3)
        lazada_search_result = HTML(html=self.browser.page_source)
        products = lazada_search_result.find('div[data-qa-locator="product-item"]')
        for product in products:
            # get the product image
            img_el = product.find('img.jBwCF', first=True)
            if img_el != None:
                product_img = f'https:{img_el.attrs["src"]}'

            # get the product name
            name_el = product.find('a[title]', first=True)
            if name_el != None:
                product_name = name_el.full_text

            # get the product link
            link_el = product.find('a[title]', first=True)
            if link_el != None:
                product_link = f'https:{link_el.attrs["href"]}'

            # redirect to product page
            sleep(2)
            self.browser.get(product_link)
            ratings_el = WebDriverWait(self.browser, 20).until(
                EC.presence_of_element_located((By.ID, 'module_product_review'))
            )
            ratings_el.location_once_scrolled_into_view
            sleep(2)
            product_page_source = HTML(html=self.browser.page_source)
            
            # get the ratings average
            ratings_avg = product_page_source.find('span.score-average', first=True)
            if ratings_avg != None:
                product_ratings_avg = float(ratings_avg.full_text)

            # get the ratings count
            ratings_count = product_page_source.find('div.count', first=True)
            if ratings_count != None:
                product_ratings_count = self.convert_ratings_count_int(ratings_count.full_text)

            # get the whole price and currency
            price = product_page_source.find('span.pdp-price.pdp-price_type_normal.pdp-price_color_orange.pdp-price_size_xl', first=True)
            if price != None:
                product_price = price.full_text
                product_price_currency = product_price[0]

            if product_img != '' and \
                product_name != '' and \
                product_link != '' and \
                product_ratings_avg != 0.0 and \
                product_ratings_count != 0 and \
                product_price != '' and \
                product_price_currency != '':
                self.result.append(
                    {
                        'name': product_name,
                        'img_url': product_img,
                        'link': product_link,
                        'ratings_avg': float(product_ratings_avg),
                        'ratings_count': int(product_ratings_count),
                        'price': product_price,
                        'currency': product_price_currency,
                        'source': self.base_url
                    }
                )

        print(f'Done scraping {self.base_url}')

    def get_result(self) -> list:
        return self.result

    # convert scrape data to csv file
    def convert_to_csv(self):
        products_df = pd.DataFrame.from_dict(self.result)
        products_df.to_csv(
            f'{self.shop}_search_{"_".join(self.keyword.split())}.csv', 
            index=False, 
            header=True
        )