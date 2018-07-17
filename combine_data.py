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
			if df_main['MI_QFIIS'].loc[index] == 0:
				ratio = get_daily_MI_QFIIS(stock, dt.year, dt.month, dt.day)
				df_main['MI_QFIIS'].at[index] = ratio
			if df_main['foreign_buy'].loc[index] == 0:
				foreign_buy, foreign_sell, trust_buy, trust_sell, dealer_buy, dealer_sell = get_daily_3j(stock, dt.year, dt.month, dt.day)
				df_main['foreign_buy'].at[index] = foreign_buy
				df_main['foreign_sell'].at[index] = foreign_sell
				df_main['trust_buy'].at[index] = trust_buy
				df_main['trust_sell'].at[index] = trust_sell
				df_main['dealer_buy'].at[index] = dealer_buy
				df_main['dealer_sell'].at[index] = dealer_sell
		print('Combin {}'.format(stock))
		df_main.to_csv('history/'+stock+'.csv')
		#break
	#print(df_main)
main()