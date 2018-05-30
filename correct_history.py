
from __future__ import print_function

import numpy as np
import pandas as pd
from googlefinance.client import get_price_data, get_prices_data, get_prices_time_data
from utility import *



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
	
#def correct_history(stock):
#	df['

def main():
	stocDict = readStockList('all_stock.csv')
	print('stocDict = ', stocDict)
	
	nonExistList = []
	for stock in stocDict:
		
		#df = get_history(stock, '5Y')
		#if stock == '2454':
		#	df['Volume'].at['2015-12-28 13:30:00'] = 2643993
		#if stock == '2448':
		df = pd.read_csv('history/'+stock+'.csv')
		
		try:
			idx = df[df['Date']=='2015-12-28 13:30:00'].index[0]
			df['Volume'].at[idx] = df['Volume'].loc[idx]/100
			print('update {}\n'.format(stock))
		except:
			nonExistList.append(stock)
			#print('{} no 2015-12-28'.format(stock))
		df.to_csv('history.new/'+stock+'.csv')
		
	for to_del in nonExistList:
		print('delete dead {}'.format(to_del))
		del stocDict[to_del]
	writeStockList('all_stock_new.csv', stocDict)
main()