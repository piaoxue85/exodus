from __future__ import print_function

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter
from talib.abstract import *
from matplotlib.dates import AutoDateFormatter, AutoDateLocator, date2num, num2date
from kd_predict import *
import talib
import argparse
from collections import OrderedDict

def readStockList(fname):
	_stock = OrderedDict()
	f = open(fname, mode='r', encoding="utf-8")
	for line in f:
		w = line.replace('\n', '').split(',')
		_stock[w[0]] = (w[0], w[1])
	f.close()
	return _stock	

def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--initial", required=False, default=1000)
	ap.add_argument("-v", "--visualize", required=False, default=False, action='store_true')
	ap.add_argument("-d", "--debug", required=False, default=False, action='store_true')
	args = vars(ap.parse_args())

	pd.options.display.float_format = '{:.2f}'.format

	stockList = readStockList('all_stock.csv')
	initial_cash = args['initial']

	for stock in stockList:
		try:
			df_main = pd.read_csv('history/'+stock+'.csv', delim_whitespace=False, header=0)
		except:
			#print('history/'+stock+'.csv has problem')
			continue
		if df_main.empty:
			continue
		# remove null data
		initial_cash = args['initial']
		df_main = df_main.dropna()
		#df_main = df_main.drop('Adj Close', 1)
		df_main['Date'] = pd.to_datetime(df_main.Date)
		df_main['DateStr'] = df_main['Date'].dt.strftime('%Y-%m-%d')
		df_main['Volume'] = df_main['Volume'] / 1000
		df_main.rename(columns={'Open': 'open', 'Close': 'close', \
								'High': 'high', 'Low': 'low', 'Volume': 'volume'
								}, inplace=True)
			
		df_main['k'], df_main['d'] = talib.STOCH(df_main['high'], df_main['low'], df_main['close'], fastk_period=9)
		df_main['RSI'] =  talib.RSI(df_main['close'], timeperiod=10)
		df_main = df_main.dropna()
		#df_main['overbought_cross'] = pd.Series(kd_find_overbought_cross(df_main))
		#df_main['oversold_cross'] = pd.Series(kd_find_oversold_cross(df_main))
		#df_main['invest_test'] = pd.Series()
		df_main.reset_index(drop=True, inplace=True)

		predict = ta_predict(df_main)
		
		ta_p0 = predict.investment_return_history(initial_cash=initial_cash, 
												max=(1, 0.15, 1, 1), \
												overbought_idx=(80, 80, 1, True), \
												oversold_idx=(22, 30, 1, True))
		ta_p0['Total'] = ta_p0['Total'] - initial_cash
		
		ta_p0.to_csv('test_result/'+stock+'_p0.csv')
		max_return_idx = ta_p0['Total'].idxmax()
		min_return_idx = ta_p0['Total'].idxmin()
		final_return = ta_p0['Total'].tail(1).values[0]
		max_return = ta_p0['Total'].loc[max_return_idx]
		min_return = ta_p0['Total'].loc[min_return_idx]
		print('========= p0 on {}, initial = {:.2f}'.format(stock, args['initial']))
		print('final earn {:.2f}({:.2f}%)'.format(final_return, (final_return*100)/initial_cash))
		print('max earn {:.2f}({:.2f}%) on {}'.format(max_return, (max_return*100)/initial_cash, ta_p0['Date'].loc[max_return_idx]))
		print('min earn {:.2f}({:.2f}%) on {}'.format(min_return, (min_return*100)/initial_cash, ta_p0['Date'].loc[min_return_idx]))

		#kd_p1 = predict.investment_return_history(initial_cash=initial_cash, 
		#										max=(1, 0.15, 10, 10), \
		#										overbought_idx=(75, 75, 10, False), \
		#										oversold_idx=(22, 30, 10, False))
		#kd_p1['Total'] = kd_p1['Total'] - initial_cash
	
	#trade_history = [('kd_p0', kd_p0), ('kd_p1', kd_p1)]
	#draw = kd_draw(stockList[args['stock']][0]+'  '+stockList[args['stock']][1], df_main, trade_history)
	#draw.draw()
	
main()