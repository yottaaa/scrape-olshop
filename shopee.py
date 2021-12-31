from requests_html import HTMLSession, Element, HTML
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.service import Service
from time import sleep
import os
import pandas as pd

class ShopeeScrape:

	def __init__(self, keyword):
		self.keyword = keyword
		self.shop = 'shopee'
		self.base_url = 'https://shopee.ph'
		webdrive_service = Service(os.environ.get('CHROME_WEBDRIVER'))
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
		# invoke the webdriver
		self.browser = webdriver.Chrome(
			executable_path=os.environ.get('CHROME_WEBDRIVER'),
			options = chrome_options
		)
		self.browser.get(f'{self.base_url}/search?keyword={self.keyword}')
		self.delay = 3 #secods

		WebDriverWait(self.browser, self.delay)
		print(f'Searching for "{self.keyword}" on {self.base_url}')
		sleep(3)

		self.result = list()

	# to check if the element has the specific attribute
	def check_attr(self, el, attr):
		try:
			el.attrs[attr]
			return True
		except KeyError:
			return False

		return True

	# convert ratings count to int
	def convert_ratings_count_int(self, ratings_count) -> int:
		remove_str = {'ratings':'','.':'','K':'00'}

		for k,v in remove_str.items():
			ratings_count = ratings_count.replace(k,v)
		 
		return int(ratings_count)


	# search result
	def search_result(self):
		product_img = ''
		product_name = ''
		product_link = ''
		product_ratings_count = ''
		product_ratings_avg = 0
		product_price = ''
		product_price_currency = ''
		
		# html = browser.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
		shopee = self.browser.page_source

		# get products
		shopee_search_result = HTML(html=shopee)
		products = shopee_search_result.find('a[data-sqe="link"]')


		for product in products:
			# get product url
			link_el = product.find('a[data-sqe="link"]', first=True)
			if link_el != None:
				product_link = self.base_url + link_el.attrs['href']

			# get name
			name_el = product.find('div[data-sqe="name"]', first=True)
			if name_el != None:
				product_name = name_el.full_text

			price_el = product.find('div._3_FVSo', first=True)
			if price_el != None:
				product_price = price_el.full_text
				product_price_currency = price_el.full_text[0]

			sleep(2)
			# get thumbnail image
			img_el = product.find('img._3-N5L6', first=True)
			if self.check_attr(img_el, 'src'):
				product_img = img_el.attrs['src']

			# redirect to the product to get the ratings
			self.browser.get(product_link)
			WebDriverWait(self.browser, self.delay)
			sleep(3)
			s_ratings = self.browser.page_source
			shopee_product_ratings = HTML(html=s_ratings)
			ratings = shopee_product_ratings.find('div.flex._1GknPu')

			if len(ratings) == 0:
				continue
			else:
				# get ratings avg
				product_ratings_avg = float(ratings[0].full_text)

				# get ratings count
				product_ratings_count = self.convert_ratings_count_int(ratings[1].full_text)

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

	# convert scrape data to csv file
	def convert_to_csv(self):
		products_df = pd.DataFrame.from_dict(self.result)
		products_df.to_csv(
			f'{self.shop}_search_{"_".join(self.keyword.split())}.csv', 
			index=False, 
			header=True
		)
