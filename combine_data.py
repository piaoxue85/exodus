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
		print('Combin {}'.format(stock))
		df_main.to_csv('history/'+stock+'.csv')
		#break
	#print(df_main)
main()