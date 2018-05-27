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

def readStockList(fname):
	_stock = dict()
	f = open(fname, mode='r', encoding="utf-8")
	for line in f:
		w = line.replace('\n', '').split(',')
		_stock[w[0]] = (w[0], w[1])
	f.close()
	return _stock	

def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("-s", "--stock", required=True)
	ap.add_argument("-v", "--visualize", required=False, default=False, action='store_true')
	ap.add_argument("-d", "--debug", required=False, default=False, action='store_true')
	args = vars(ap.parse_args())

	pd.options.display.float_format = '{:.2f}'.format

	stockList = readStockList('stock.csv')

	df_main = pd.read_csv('history/'+args['stock']+'.csv', delim_whitespace=False, header=0)
	# remove null data
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
	
	kd_p0 = predict.investment_return_history(initial_cash=1000, 
											max=(1, 0.15, 1, 1), \
											overbought_idx=(80, 80, 1, True), \
											oversold_idx=(22, 30, 1, True))
	kd_p0['Total'] = kd_p0['Total'] - 1000

	kd_p1 = predict.investment_return_history(initial_cash=1000, 
											max=(1, 0.15, 10, 10), \
											overbought_idx=(75, 75, 10, False), \
											oversold_idx=(22, 30, 10, False))
	kd_p1['Total'] = kd_p1['Total'] - 1000

	#print(kd_p0)

	#period = 1
	#self.df = df_main.loc[range(0, len(df_main), period)]
	#self.df.reset_index(drop=True, inplace=True)
	
	trade_history = [('kd_p0', kd_p0), ('kd_p1', kd_p1)]
	draw = kd_draw(stockList[args['stock']][0]+'  '+stockList[args['stock']][1], df_main, trade_history)
	draw.draw()
	
main()