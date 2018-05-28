
from __future__ import print_function

import numpy as np
import pandas as pd
from googlefinance.client import get_price_data, get_prices_data, get_prices_time_data


def readStockList(fname):
	_stock = dict()
	f = open(fname, mode='r', encoding="utf-8")
	for line in f:
		w = line.replace('\n', '').split(',')
		_stock[w[0]] = (w[0], w[1])
	f.close()
	return _stock	


def get_history(stock, period):
	param = {
	    'q': stock, 		# Stock symbol (ex: "AAPL")
	    'i': "86400", 		# Interval size in seconds ("86400" = 1 day intervals)
	    #'i': "300", 		# Interval size in seconds ("86400" = 1 day intervals)
	    'x': "TPE", 		# Stock exchange symbol on which stock is traded (ex: "NASD")
	    'p': period 			# Period (Ex: "1Y" = 1 year)
	}

	df = get_price_data(param)
	return df

def main():
	stocDict = readStockList('all_stock.csv')
	print('stocDict = ', stocDict)
	for stock in stocDict:
		
		df = get_history(stock, '5Y')
		#if stock == '2454':
		#	df['Volume'].at['2015-12-28 13:30:00'] = 2643993
		#if stock == '2448':
		print('Get {}'.format(stock))
		try:
			df['Volume'].at['2015-12-28 13:30:00'] = df['Volume'].loc['2015-12-28 13:30:00']/10
		except:
			print('2015-12-28 13:30:00 not exist')
		df['Date'] = df.index
		df.reset_index()
		print(df.to_csv('history/'+stock+'.csv'))

main()