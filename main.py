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

def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("-f", "--file", required=True)
	ap.add_argument("-v", "--visualize", required=False, default=False, action='store_true')
	ap.add_argument("-d", "--debug", required=False, default=False, action='store_true')
	args = vars(ap.parse_args())

	pd.options.display.float_format = '{:.2f}'.format

	df_main = pd.read_csv(args["file"], delim_whitespace=False, header=0)
	# remove null data
	df_main = df_main.dropna()
	df_main = df_main.drop('Adj Close', 1)
	df_main['Date'] = pd.to_datetime(df_main.Date)
	df_main['DateStr'] = df_main['Date'].dt.strftime('%Y-%m-%d')
	df_main.rename(columns={'Open': 'open', 'Close': 'close', \
							'High': 'high', 'Low': 'low', 'Volume': 'volume'
							}, inplace=True)
		
	df_main['k'], df_main['d'] = talib.STOCH(df_main['high'], df_main['low'], df_main['close'], fastk_period=9)
	df_main = df_main.dropna()
	#df_main['overbought_cross'] = pd.Series(kd_find_overbought_cross(df_main))
	#df_main['oversold_cross'] = pd.Series(kd_find_oversold_cross(df_main))
	#df_main['invest_test'] = pd.Series()
	df_main.reset_index(drop=True, inplace=True)

	predict = kd_predict(df_main, initial_cash=100, max=(1, 0.15, 10, 10), \
				overbought_idx=(80, 80, 10, False), oversold_idx=(22, 30, 10, False))
	
	trade_history = predict.investment_return_history()
	#trade_history['Total'] = trade_history['Total'] - 100
	#print(trade_history)

	period = 1
	df_period = df_main.loc[range(0, len(df_main), period)]
	df_period.reset_index(drop=True, inplace=True)


main()