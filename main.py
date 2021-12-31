from amazon import AmazonScrape
from shopee import ShopeeScrape
from time import sleep
import sys
import pandas as pd
import numpy as np

def bayes_average():
	return

def analysis(data):
	return trnsfrm
	d_data

def main():
	result = list()
	keyword = ''
	if len(sys.argv) == 2:
		print(sys.argv[1])
		keyword = sys.argv[1]

		amazon_search = AmazonScrape(keyword)
		amazon_search.search_result()
		sleep(1)
		shopee_search = ShopeeScrape(keyword)
		shopee_search.search_result()

		result = amazon_search.get_result() + shopee_search.get_result() 

		print(result)
		shop_df = pd.DataFrame.from_dict(result)
		shop_df = shop_df.sort_values(by='ratings_count', ascending=False)


		shop_df.to_csv(
			f'olshop_scrape_search_{"_".join(keyword.split())}.csv', 
			index=False, 
			header=True
		)

if __name__ == '__main__':
	main()