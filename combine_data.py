from __future__ import print_function

import argparse
import numpy as np
import pandas as pd
from collections import OrderedDict
from utility import *

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("-f", "--file", required=False, default='all_stock.csv')
	ap.add_argument("-d", "--debug", required=False, default=False, action='store_true')
	args = vars(ap.parse_args())

	pd.options.display.float_format = '{:.2f}'.format

	stockList = readStockList(args['file'])
	for stock in stockList:
		stock = '1101'
		empty, df_main = readStockHistory(stock, 9999, raw=True)
		if empty == True:
			continue
		for index, row in df_main.iterrows():
			dt = row['Date']
			#print('get {} of {}-{}-{}'.format(stock, dt.year, dt.month, dt.day))			
			#eps = get_daily_eps(stock, dt.year, dt.month, dt.day)
			eps = get_daily_eps(stock, dt.year, dt.month, dt.day)
			revenue = get_monthly_revenus(stock, dt.year, dt.month)
			#print('get {} of {}-{}-{} eps {} revenus {}'.format(stock, dt.year, dt.month, dt.day, eps, revenue))
			df_main['eps'].at[index] = eps
			df_main['revenue'].at[index] = revenue
		print('Combin {}'.format(stock))
		df_main.to_csv('history_combine/'+stock+'.csv')
		break
	#print(df_main)
main()