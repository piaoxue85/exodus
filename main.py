from __future__ import print_function

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter
from talib.abstract import *
from matplotlib.dates import AutoDateFormatter, AutoDateLocator, date2num, num2date
from kd_predict import *
from utility import *
import talib
import argparse
from collections import OrderedDict
import datetime

def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--initial", required=False, default=1000)
	ap.add_argument("-v", "--visualize", required=False, default=False, action='store_true')
	ap.add_argument("-d", "--debug", required=False, default=False, action='store_true')
	args = vars(ap.parse_args())

	pd.options.display.float_format = '{:.2f}'.format

	stockList = readStockList('all_stock.csv')
	initial_cash = args['initial']
	
	now = datetime.datetime.now()

	for stock in stockList:
		initial_cash = args['initial']
		empty, df_main = readStockHistory(stock)
		if empty == True:
			continue

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
		trade_history = [('ta_p0', ta_p0)]
		pngName = 'figures/{}_{}{:02d}{:02d}.png'.format(stock, now.year, now.month, now.day)
		#pngName = None
		draw = kd_draw(stockList[stock][0]+'  '+stockList[stock][1], df_main, trade_history, pngName)
		draw.draw()
		df_short = df_main.tail(200)
		df_short.reset_index(drop=True, inplace=True)
		ta_p0_short = ta_p0.tail(200)
		ta_p0_short.reset_index(drop=True, inplace=True)
		trade_history = [('ta_p0', ta_p0_short)]
		pngName = 'figures/{}_{}{:02d}{:02d}_01.png'.format(stock, now.year, now.month, now.day)
		draw = kd_draw(stockList[stock][0]+'  '+stockList[stock][1], df_short, trade_history, pngName)
		draw.draw()
		break
		
main()