from __future__ import print_function

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter
from talib.abstract import *
from matplotlib.dates import AutoDateFormatter, AutoDateLocator, date2num, num2date
from ta_predict import *
from utility import *
import talib
import argparse
from collections import OrderedDict
import datetime
import json

def readPolicy(path):
	json_data=open(path)
	policy = json.load(json_data)
	return policy
														
def main(args):

	pd.options.display.float_format = '{:.2f}'.format

	stockList = readStockList(args['file'])
	if (args['stock'] != ''):
		_stockList = OrderedDict()
		_stockList[args['stock']] = stockList[args['stock']]
		stockList = _stockList
		#stockList = [(args['stock'], '華晶科')]

	df_ROE=readROEHistory('ROE_2006_2017.csv')
	stockROEList = df_ROE['stock'].values
	
	now = datetime.datetime.now()

	policy = readPolicy('policy/'+args['evaluate'])
	period = policy['period']
	pngPath = args['path']+'/png'
	evaluatePath = args['path']+'/'+args['evaluate'].split('.')[0]
	os.makedirs(pngPath, exist_ok=True)
	os.makedirs(evaluatePath, exist_ok=True)

	df_div_eng, _ = readDividenHistory('dividen.csv')
	invest_return_columns = ['stock', 'name', 'final%', 'max%', 'max_date', 'min%', 'min_date']
	df_invest_return = pd.DataFrame(columns=invest_return_columns)
	for stock in stockList:

		#if (stock not in stockROEList) and (args['stock'] == ''):
		#	print('skip ', stock)
		#	continue
		#print('process ', stock)
		initial_cash = policy['initial']
		empty, df_main = readStockHistory(stock, period, raw=False)
		if empty == True:
			print('no data')
			continue
		(stock_id, stock_name) = stockList[stock]
		if (args['evaluate'] != ''):
			predict = ta_predict(stock_id, df_main)
			
			buy_tactics = []
			for idx in range(0, policy['buy_tactic_num']):
				buy_tactics.append(policy['buy_tactics_'+str(idx)])
			sell_tactics = []
			for idx in range(0, policy['sell_tactic_num']):
				sell_tactics.append(policy['sell_tactics_'+str(idx)])
				
			ta_p0 = predict.investment_return_history_by_policy(policy['initial'], 
												buy_tactics, \
												sell_tactics);

			ta_p0['Total'] = ta_p0['Total'] - initial_cash
			
			ta_p0.to_csv(evaluatePath+'/'+stock+policy['name']+'.csv')
			max_return_idx = ta_p0['Total'].idxmax()
			min_return_idx = ta_p0['Total'].idxmin()
			final_return = ta_p0['Total'].tail(1).values[0]
			max_return = ta_p0['Total'].loc[max_return_idx]
			min_return = ta_p0['Total'].loc[min_return_idx]
			
			minDate = '{}-{}-{}'.format(ta_p0['Date'].loc[min_return_idx].year, \
										ta_p0['Date'].loc[min_return_idx].month, \
										ta_p0['Date'].loc[min_return_idx].day)
			maxDate = '{}-{}-{}'.format(ta_p0['Date'].loc[max_return_idx].year, \
										ta_p0['Date'].loc[max_return_idx].month, \
										ta_p0['Date'].loc[max_return_idx].day)
			_invest_return = pd.DataFrame(
									[[stock_id, stock_name, 
									(final_return*100)/initial_cash, 
									(max_return*100)/initial_cash, maxDate, 
									(min_return*100)/initial_cash, minDate]],
									columns=invest_return_columns)
			df_invest_return = df_invest_return.append(_invest_return, ignore_index=True)
			print('========= {} on {} {}, initial = {:.2f}'.format(policy['name'], stock_id, stock_name, initial_cash))
			print('final earn {:.2f}({:.2f}%)'.format(final_return, (final_return*100)/initial_cash))
			print('max earn {:.2f}({:.2f}%) on {}'.format(max_return, (max_return*100)/initial_cash, ta_p0['Date'].loc[max_return_idx]))
			print('min earn {:.2f}({:.2f}%) on {}'.format(min_return, (min_return*100)/initial_cash, ta_p0['Date'].loc[min_return_idx]))

			trade_history = [(policy['name'], ta_p0)]
		
			pngName = evaluatePath+'/{}_{}{:02d}{:02d}.png'.format(stock, now.year, now.month, now.day)
			draw = ta_draw(stock_id+'  '+stock_name, df_main, trade_history, pngName)
			draw.draw()
			
			df_short = df_main.tail(20)
			df_short.reset_index(drop=True, inplace=True)
			ta_p0_short = ta_p0.tail(20)
			ta_p0_short.reset_index(drop=True, inplace=True)
			trade_history = [(policy['name'], ta_p0_short)]
			pngName = evaluatePath+'/{}_{}{:02d}{:02d}_01.png'.format(stock, now.year, now.month, now.day)
			draw = ta_draw(stock_id+'  '+stock_name, df_short, trade_history, pngName)
			draw.draw()
			del draw
			
		if args['tindex'] == True:
			df_short = df_main.tail(20)
			df_short.reset_index(drop=True, inplace=True)
			
			pngName = pngPath+'/{}_{}{:02d}{:02d}_short.png'.format(stock, now.year, now.month, now.day)
			draw = ta_draw(stock_id+'  '+stock_name, df_short, None, pngName)
			draw.draw()
			pngName = pngPath+'/{}_{}{:02d}{:02d}_KD.png'.format(stock, now.year, now.month, now.day)
			draw.draw_ta('KD', pngName)
			pngName = pngPath+'/{}_{}{:02d}{:02d}_MACD.png'.format(stock, now.year, now.month, now.day)
			draw.draw_ta('MACD', pngName)
			pngName = pngPath+'/{}_{}{:02d}{:02d}_SMA.png'.format(stock, now.year, now.month, now.day)
			draw.draw_ta('SMA', pngName)
			pngName = pngPath+'/{}_{}{:02d}{:02d}_BIAS.png'.format(stock, now.year, now.month, now.day)
			draw.draw_ta('BIAS', pngName)
			del draw
	
	if df_invest_return.empty == False:
		df_invest_return = df_invest_return.sort_values(by=['final%'], ascending=False)
		df_invest_return.to_csv(evaluatePath+'/total_return.csv', float_format='%.2f')
		writer = pd.ExcelWriter(evaluatePath+'/total_return.xlsx')
		df_invest_return.to_excel(writer, float_format='%.2f')
		writer.save()		

if __name__ == '__main__':

	ap = argparse.ArgumentParser()
	ap.add_argument("-f", "--file", required=False, default='all_stock.csv')
	ap.add_argument("-s", "--stock", required=False, default='')
	ap.add_argument("-v", "--visualize", required=False, default=False, action='store_true')
	ap.add_argument("-t", "--tindex", required=False, default=False, action='store_true')
	ap.add_argument("-p", "--path", required=False, default=False, action='store_true')
	ap.add_argument("-e", "--evaluate", required=False, default='')
	ap.add_argument("-g", "--graphics", required=False, default=False, action='store_true')
	ap.add_argument("-d", "--debug", required=False, default=False, action='store_true')
	args = vars(ap.parse_args())

	main(args)