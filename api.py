from shops.amazon import AmazonScrape
from shops.shopee import ShopeeScrape
from shops.lazada import LazadaScrape
import pandas as pd
import numpy as np
from time import sleep
from datetime import datetime

def bayes_average(r_count, r_avg, c, m) -> float:
	return float((r_count*r_avg + m*c)/(r_count+c))

def convert_to_csv(keyword,lst):
	new_df = pd.DataFrame.from_dict(lst)
	new_df.to_csv(
		f'results\\olshop_search_{"_".join(keyword.split())}_{datetime.now().strftime("%m%d%Y_%H%M%S")}.csv', 
		index=False, 
		header=True
	)
	print('\nconvert to csv done.')

def transformed_data(df) -> dict:
	
	products = list()
	count = 0

	# insert the sorted data with bayes average
	data = list()
	m = df['ratings_avg'].mean()
	c = np.percentile(
		[row.ratings_count for row in df.itertuples()], 
		25
	)
	for row in df.itertuples():
		b_avg = bayes_average(row.ratings_count,row.ratings_avg,c,m)
		data.append(
			{
				'name': row.name,
				'img_url': row.img_url,
				'link': row.link,
				'ratings_avg': row.ratings_avg,
				'ratings_count': row.ratings_count,
				'bayes_avg': b_avg,
				'price': row.price,
				'currency': row.currency,
				'source': row.source
			}
		)

	# sort data by bayes average
	data_df = pd.DataFrame.from_dict(data)
	data_df = data_df.sort_values(by='bayes_avg', ascending=False)

	# insert new data
	for idx, row in enumerate(data_df.itertuples()):
		products.append(
			{
				'id': idx,
				'name': row.name,
				'img_url': row.img_url,
				'link': row.link,
				'ratings_avg': row.ratings_avg,
				'ratings_count': row.ratings_count,
				'bayes_avg': row.bayes_avg,
				'price': row.price,
				'currency': row.currency,
				'source': row.source
			}
		)



	return {
		'products': products,
		'count': len(products)
	}

def clean_data(raw_data) -> list:
	new_data = []
	for item in raw_data:
		if item['name'] != '' and \
			item['link'] != '' and \
			item['ratings_avg'] != 0.0 and \
			item['ratings_count'] != 0 and \
			item['price'] != '' and \
			item['currency'] != '':
			new_data.append(item)

	return new_data

def search(keyword) -> dict:
	result = []

	# scraping
	amz = AmazonScrape(keyword)
	amz.search_result()
	amz.browser.quit()
	result += amz.get_result()
	sleep(1)
	shp = ShopeeScrape(keyword)
	shp.search_result()
	shp.browser.quit()
	result += shp.get_result()
	sleep(1)
	laz = LazadaScrape(keyword)
	laz.search_result()
	laz.browser.quit()
	result += laz.get_result()
	sleep(2)

	# clean data
	# cleaned_data = clean_data(result)
	cleaned_data = result

	# convert result to a dataframe
	olshop_df = pd.DataFrame.from_dict(cleaned_data)

	# sort by ratings count
	olshop_df = olshop_df.sort_values(by='ratings_count', ascending=False)

	# transform data to a response data
	new_data = transformed_data(olshop_df)
	return new_data