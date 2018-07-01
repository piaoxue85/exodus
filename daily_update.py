
from __future__ import print_function

import numpy as np
import pandas as pd
import argparse
from utility import *


def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("-t", "--type", required=False, default='price')
	ap.add_argument("-s", "--start", required=False, default='today')
	ap.add_argument("-p", "--period", required=False, default='1d')
	args = vars(ap.parse_args())	
	
	stockList = readStockList('all_stock.csv')
	dtype = args['type']
	if args['start'] != 'today':
		startDate = date(int(args['start'].split('-')[0]), int(args['start'].split('-')[1]), int(args['start'].split('-')[2]))
	else:
		startDate = date.today()
	period = args['period']

	update_monthly_report(startDate.year, startDate.month)
	update_daily(startDate, period)

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


main()