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

		empty, df_main = readStockHistory(stock, 9999, raw=True)
		if empty == True:
			continue
		for index, row in df_main.iterrows():
			dt = row['Date']
			#print('get {} of {}-{}-{}'.format(stock, dt.year, dt.month, dt.day))			
			#eps = get_daily_eps(stock, dt.year, dt.month, dt.day)
			if df_main['PER'].loc[index] == 0:
				per = get_daily_per(stock, dt.year, dt.month, dt.day)
				df_main['PER'].at[index] = per
			if df_main['revenue'].loc[index] == 0:
				revenue = get_monthly_revenus(stock, dt.year, dt.month)
				df_main['revenue'].at[index] = revenue
		print('Combin {}'.format(stock))
		df_main.to_csv('history/'+stock+'.csv')
		#break
	#print(df_main)
main()