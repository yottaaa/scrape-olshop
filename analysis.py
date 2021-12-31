import pandas as pd
import numpy as np

def bayesian_average(C, M, r_avg, r_count) -> float:
	return float((r_count*r_avg + M*C)/(r_count+C))

olshop_data = pd.read_csv('olshop_scrape_search_iphone_X.csv')
# olshop_data = pd.DataFrame.from_dict(data)
olshop_data = olshop_data.sort_values(by='ratings_count', ascending=False)
ratings_count = [row.ratings_count for row in olshop_data.itertuples()]
print(ratings_count)
M = olshop_data['ratings_avg'].mean()
C = np.percentile(ratings_count, 25)
print(f'M = {M}, C = {C}')


trnsfrmd_data = list()
for row in olshop_data.itertuples():
	b_avg = bayesian_average(C,M,row.ratings_avg,row.ratings_count)
	trnsfrmd_data.append(
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

new_olshop_data = pd.DataFrame.from_dict(trnsfrmd_data)
new_olshop_data = new_olshop_data.sort_values(by='bayes_avg',ascending=False)
print(new_olshop_data)

new_olshop_data.to_csv(
	'new_olshop_scrape_search_iphone_X.csv',
	index=False,
	header=True
)