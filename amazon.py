from requests_html import HTMLSession, Element, HTML
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os
import pandas as pd

class AmazonScrape:

	def __init__(self, keyword):
		self.keyword = ""
		if len(keyword.split()) == 1:
			self.keyword  = keyword
		else:
			self.keyword  = "+".join(keyword.split())

		self.shop = "amazon"
		self.base_url = 'https://www.amazon.com'
		chrome_options = Options()

		# set chrome driver options to disable any popup's from the website
		# to find local path for chrome profile, open chrome browser
		# and in the address bar type, "chrome://version"
		chrome_options.add_argument('disable-notifications')
		chrome_options.add_argument('--disable-infobars')
		chrome_options.add_argument('start-maximized')
		chrome_options.add_argument("--headless")
		# To disable the message, "Chrome is being controlled by automated test software"
		chrome_options.add_argument("disable-infobars")
		# Pass the argument 1 to allow and 2 to block
		chrome_options.add_experimental_option("prefs", { 
		    "profile.default_content_setting_values.notifications": 2
		    })
		self.browser = webdriver.Chrome(
			executable_path=os.environ['CHROME_WEBDRIVER'],
			options=chrome_options
		)
		self.browser.get(self.base_url)

		WebDriverWait(self.browser, 5)

		self.search_el = self.browser.find_element(By.ID, 'twotabsearchtextbox')
		self.search_el.send_keys(self.keyword)
		self.search_el.send_keys(Keys.RETURN)
		print(f'Searching for "{self.keyword}" on {self.base_url}')

		self.result = list()

	def ranking(self, res) -> list:
		pass 

	def check_float(self, deci) -> bool:
		try:
			float(deci)
			return True
		except ValueError:
			return False

		return False

	def search_result(self):
		product_img = ''
		product_link = ''
		product_name = ''
		product_price = ''
		product_ratings_avg = 0.0
		product_ratings_count = 0
		product_price_currency = ''

		# get products
		amazon_search_result = HTML(html=self.browser.page_source)
		products = amazon_search_result.find('div[data-component-type="s-search-result"]')

		for product in products:
			# get the product name
			name_el = product.find('a.a-link-normal.s-link-style.a-text-normal', first=True)
			if name_el != None:
				product_name = name_el.full_text

			# get the product link
			link_el = product.find('a.a-link-normal.s-link-style.a-text-normal', first=True)
			if link_el != None:
				product_link = self.base_url + link_el.attrs['href']

			# get img url
			img_el = product.find('img.s-image', first=True)
			if img_el != None:
				product_img = img_el.attrs['src']

			# get ratings
			ratings_el = product.find('span[aria-label]')
			if ratings_el != None:
				if len(ratings_el) == 2:
					# get the average ratings
					r_avg = ratings_el[0].attrs['aria-label'].split()[0]
					if self.check_float(r_avg) == True:
						product_ratings_avg = r_avg
					# get the ratings count
					r_count = ratings_el[1].attrs['aria-label'].replace(',','')
					product_ratings_count = r_count


			# get the price
			price_el = product.find('span.a-price')
			if price_el != None:
				if len(price_el) == 2:
					# get the whole price
					w_price = price_el[0].full_text
					product_price = w_price
					# get the currency
					product_price_currency = w_price[0]

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
		
		self.browser.close()
		print(f'Done scraping {self.base_url}')

	def get_result(self) -> list:
		return self.result

	def convert_to_csv(self):
		# convert search result to csv file
		products_df = pd.DataFrame.from_dict(self.result)
		products_df.to_csv(
			f'{self.shop}_search_{"_".join(self.keyword.split("+"))}.csv', 
			index=False, 
			header=True
		)

amazon_search = AmazonScrape("headphone")
amazon_search.search_result()
print(amazon_search.get_result())
# amazon_search.convert_to_csv()

