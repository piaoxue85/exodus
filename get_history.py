
from __future__ import print_function

import numpy as np
import pandas as pd
import argparse
from utility import *




def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("-d", "--data", required=False, default='all')
	ap.add_argument("-p", "--period", required='1d', default=200)
	ap.add_argument("-a", "--append", required=False, default=True)
	args = vars(ap.parse_args())	
	
	stocDict = readStockList('all_stock.csv')
	print('stocDict = ', stocDict)
	dtype = args['data']
	period = args['period']
	append = args['append']

	if dtype == 'all' or dtype == 'price':
		for stock in stocDict:
			
			df = update_stock_history(stock, period)
			print('Get {} stock price'.format(stock))
			if period == '5Y':
				try:
					df['Volume'].at['2015-12-28 13:30:00'] = df['Volume'].loc['2015-12-28 13:30:00']/10
				except:
					print('2015-12-28 13:30:00 no exist')				
			df['Date'] = df.index
			df.reset_index()
			if append == True:
				_text = df.to_csv(header=False)
				f = open('history/'+stock+'.csv', mode='a', encoding="utf-8")
				f.write(_text)
				f.close()
			else:
				df.to_csv('history/'+stock+'.csv')

	if dtype == 'all' or dtype == 'eps':
		update_daily_eps_period(period)

main()