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

#def draw_divi(stock, df_div_hi)

def output_div(stock, df_main, df_div_all):
	df = df_div_all.loc[df_div_all['stock'] == stock]
	_field = ['cash', 'stock', 'yield', 'payout_ratio']
	cash_list = []
	stock_list = []
	payout_list = []
	yield_list = []
	eps_list = []
	year_list = []
	for year in range(2006, 2019):
		#df_eps =
		year_list.append(year)
		cash_list.append(df['div_'+str(year)+'_cash'].values[0])
		stock_list.append(df['div_'+str(year)+'_stock'].values[0])
		payout_list.append(df['payout_ratio_'+str(year)].values[0])
		yield_list.append(df['yield_'+str(year)].values[0])
		#eps_list.append(df['div_'+str(year)+'_cash'].values[0]+df['div_'+str(year)+'_stock'].values[0]+1)
		eps_list.append(df['eps_'+str(year)].values[0])
		
	df = pd.DataFrame(	{	
						'year': year_list, 
						'cash': cash_list, 
						'stock': stock_list, 
						'yield':yield_list,
						'payout':payout_list,
						'eps':eps_list,
						})
	df.set_index('year', inplace=True)
	print('')
	return df
					
def draw_info_div1(df_info, title, pngName):
	#ax0 = plt.subplot(111)
	minEPS = df_info['eps'].min()
	maxEPS = df_info['eps'].max()
	_text = 'EPS {:.1f} ~ {:.1f}'.format(minEPS, maxEPS)

	if False:
		for index, row in df_info.iterrows():
			if row['eps'] >= (row['stock'] + row['cash']):
				row['eps'] = row['eps'] - row['stock'] - row['cash']
			else:
				if row['cash'] >= row['eps']:
					row['cash'] = row['cash'] - row['eps']
				else:
					row['stock'] = row['stock'] - row['eps']
	
	#df_info['eps'] = df_info['eps'] - df_info['stock'] - df_info['cash']
	df_info['股息'] = df_info['cash']
	df_info['股利'] = df_info['stock']
	#ax0 = df_info.plot(y=['eps','股息', '股利'], title=title, kind='bar', grid=True, stacked=True)
	ax0 = df_info.plot(y=['股息', '股利'], title=title, kind='bar', grid=True, stacked=True)
	ax0_1 = ax0.twinx()
	ax0_1.bar(df_info.index+5, df_info['eps'])
	ax0.title.set_size(24)
	ax0.text(0, 1.01, _text, transform=ax0.transAxes, fontsize=18)
	if pngName != None:
		plt.savefig(pngName)
	else:
		plt.show()	
		
def draw_info_div0(df_info, title, pngName):

	minEPS = df_info['eps'].min()
	maxEPS = df_info['eps'].max()
	_text = 'EPS {:.1f} ~ {:.1f}'.format(minEPS, maxEPS)

	df_info['股息'] = df_info['cash']
	df_info['股利'] = df_info['stock']

	bar_width = 0.35
	fig, ax0 = plt.subplots()
	ax0.bar(df_info.index-bar_width/2, df_info['股息'], bar_width,
			color='b',
            label='股息')
	ax0.bar(df_info.index-bar_width/2, df_info['股利'], bar_width,
			color='g', bottom=df_info['股息'],
            label='股利')			
	ax0.bar(df_info.index+bar_width/2, df_info['eps'], bar_width,
			color='r',
            label='eps')

	ax0.set_title(title)
	ax0.title.set_size(24)
	plt.xticks(df_info.index)
	ax0.text(0, 1.01, _text, transform=ax0.transAxes, fontsize=18)
	ax0.legend(fontsize=16)
	if pngName != None:
		plt.savefig(pngName)
	else:
		plt.show()			
					
def main(args):

	pd.options.display.float_format = '{:.2f}'.format

	stockList = readStockList(args['file'])
	if (args['stock'] != ''):
		_stockList = OrderedDict()
		_stockList[args['stock']] = stockList[args['stock']]
		stockList = _stockList
		#stockList = [(args['stock'], '華晶科')]

	now = datetime.datetime.now()

	#policy = readPolicy('policy/'+args['evaluate'])
	#period = policy['period']
	period = 2000
	pngPath = args['path']+'/png'
	evaluatePath = args['path']+'/'+args['evaluate'].split('.')[0]
	os.makedirs(pngPath, exist_ok=True)
	os.makedirs(evaluatePath, exist_ok=True)

	df_div_all, _ = readDividenHistory('dividen.csv')
	for stock in stockList:

		empty, df_main = readStockHistory(stock, period, raw=False)
		if empty == True:
			print('no data')
			continue
		(stock_id, stock_name) = stockList[stock]
		df_div = output_div(stock_id, df_main, df_div_all)

		stockPath = evaluatePath + stock
		os.makedirs(stockPath, exist_ok=True)
		pngName = stockPath+'/price_volume.png'
		draw = ta_draw(stock_id+'  '+stock_name, df_main, None, pngName)
		draw.draw_price_volume()		

		# draw PER
		pngName = stockPath+'/PER.png'
		draw.draw_ta('PER', pngName)
		
		# draw PER
		pngName = stockPath+'/revenue.png'
		draw.draw_ta('revenue', pngName)

		for p in [240, 120, 60, 30]:
			df_short = df_main.tail(p)
			df_short.reset_index(drop=True, inplace=True)
			pngName = stockPath+'/price_volume_'+str(p)+'.png'
			draw = ta_draw(stock_id+'  '+stock_name, df_short, None, pngName)
			draw.draw_price_volume(str(p))
		
		pngName = stockPath+'/EPS.png'
		draw_info_div(df_div, stock_id+'  '+stock_name + ' 股利', pngName)
		
		
if __name__ == '__main__':

	ap = argparse.ArgumentParser()
	ap.add_argument("-f", "--file", required=False, default='all_stock.csv')
	ap.add_argument("-s", "--stock", required=False, default='')
	ap.add_argument("-p", "--path", required=False, default=False, action='store_true')
	ap.add_argument("-d", "--debug", required=False, default=False, action='store_true')
	args = vars(ap.parse_args())

	main(args)