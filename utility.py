from __future__ import print_function

import numpy as np
import pandas as pd
from kd_predict import *
from collections import OrderedDict


def readStockList(fname):
	_stock = dict()
	f = open(fname, mode='r', encoding="utf-8")
	for line in f:
		w = line.replace('\n', '').split(',')
		_stock[w[0]] = (w[0], w[1])
	f.close()
	return dict(sorted(_stock.items()))

def writeStockList(fname, stockDict):
	_stock = dict()
	f = open(fname, mode='w', encoding="utf-8")
	for stock in stockDict:
		(id, name) = stockDict[stock]
		f.write('{},{}\n'.format(id, name))
	f.close()
	
def readStockHistory(stock):
	try:
		df_main = pd.read_csv('history/'+stock+'.csv', delim_whitespace=False, header=0)
	except:
		#print('history/'+stock+'.csv has problem')
		return True, None
		
	if df_main.empty:
		return True, None

	df_main = df_main.dropna()
	df_main['Date'] = pd.to_datetime(df_main.Date)
	df_main['DateStr'] = df_main['Date'].dt.strftime('%Y-%m-%d')
	df_main['Volume'] = df_main['Volume'] / 1000
	df_main.rename(columns={'Open': 'open', 'Close': 'close', \
							'High': 'high', 'Low': 'low', 'Volume': 'volume'
							}, inplace=True)
		
	df_main['k'], df_main['d'] = talib.STOCH(df_main['high'], df_main['low'], df_main['close'], fastk_period=9)
	df_main['RSI'] =  talib.RSI(df_main['close'], timeperiod=10)
	df_main = df_main.dropna()
	df_main.reset_index(drop=True, inplace=True)
	
	return False, df_main
	