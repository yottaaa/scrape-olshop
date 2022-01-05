from api import search, convert_to_csv
import sys
import pandas as pd
import numpy as np

def main():
	result = list()
	keyword = ''
	if len(sys.argv) == 2:
		print(sys.argv[1])
		keyword = sys.argv[1]

		results = search(keyword)
		print(results)
		convert_to_csv(keyword,results['products'])

if __name__ == '__main__':
	main()