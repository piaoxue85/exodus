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
import os.path
import text2png
from sklearn.preprocessing import MinMaxScaler
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
		
def draw_info_div(df_info, title, pngName):

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
	ax0.grid()
	if pngName != None:
		plt.savefig(pngName)
	else:
		plt.show()
		
		
def draw_share_holders(stock, df_price, title, pngName):

	try:
		df_raw = pd.read_csv('history/share/{}.csv'.format(stock))
	except:
		print('unable to read history/share/{}.csv'.format(stock))
		return

	_columns = [	'Date', '1-10', '11-50', '51-100', '101-200', '201-1000', '1001-', \
					'1-10(%)', '11-50(%)', '51-100(%)', '101-200(%)', '201-1000(%)', '1001-(%)',\
					'1-10(d%)', '11-50(d%)', '51-100(d%)', '101-200(d%)', '201-1000(d%)', '1001-(d%)'
				]
	df_share = pd.DataFrame(columns=_columns)
	dateList = np.unique(df_raw['日期'].values)
	

	
	for d in dateList:
		df = df_raw[df_raw['日期']==d]
		#df.rename(columns={	'比例': 'percent'})
		grp1_10 = (df[df['持股']=='1-999']['人數'].values[0] + df[df['持股']=='1000-5000']['人數'].values[0] + df[df['持股']=='5001-10000']['人數'].values[0])
		grp11_50 = (df[df['持股']=='10001-15000']['人數'].values[0] + df[df['持股']=='15001-20000']['人數'].values[0] + df[df['持股']=='20001-30000']['人數'].values[0] + \
					df[df['持股']=='30001-40000']['人數'].values[0] + df[df['持股']=='40001-50000']['人數'].values[0])
		grp51_100 = df[df['持股']=='50001-100000']['人數'].values[0]
		grp101_200 = df[df['持股']=='100001-200000']['人數'].values[0]
		grp201_1k = (df[df['持股']=='200001-400000']['人數'].values[0] + df[df['持股']=='400001-600000']['人數'].values[0] +\
						df[df['持股']=='400001-600000']['人數'].values[0] + df[df['持股']=='600001-800000']['人數'].values[0] +\
						df[df['持股']=='800001-1000000']['人數'].values[0])
		
		grp1k = df[df['持股']=='1000001']['人數'].values[0]

		grp1_10_p = (df[df['持股']=='1-999']['比例'].values[0] + df[df['持股']=='1000-5000']['比例'].values[0] + df[df['持股']=='5001-10000']['比例'].values[0])
		grp11_50_p = (df[df['持股']=='10001-15000']['比例'].values[0] + df[df['持股']=='15001-20000']['比例'].values[0] + df[df['持股']=='20001-30000']['比例'].values[0] + \
					df[df['持股']=='30001-40000']['比例'].values[0] + df[df['持股']=='40001-50000']['比例'].values[0])
		grp51_100_p = df[df['持股']=='50001-100000']['比例'].values[0]
		grp101_200_p = df[df['持股']=='100001-200000']['比例'].values[0]
		grp201_1k_p = (df[df['持股']=='200001-400000']['比例'].values[0] + df[df['持股']=='400001-600000']['比例'].values[0] +\
						df[df['持股']=='400001-600000']['比例'].values[0] + df[df['持股']=='600001-800000']['比例'].values[0] +\
						df[df['持股']=='800001-1000000']['比例'].values[0])
		
		grp1k_p = (df[df['持股']=='1000001']['比例'].values[0])
		valList = [d, grp1_10, grp11_50, grp51_100, grp101_200, grp201_1k, grp1k, \
					grp1_10_p, grp11_50_p, grp51_100_p, grp101_200_p, grp201_1k_p, grp1k_p,\
					0,0,0,0,0,0]
		_new = pd.DataFrame([valList],columns=_columns)
		df_share = df_share.append(_new, ignore_index=True)
		
	df_share = df_share.sort_values(by=['Date'], ascending=True)
	print(df_share)
	
	_text = '中位數 '
	_mean = np.median(df_share['1-10(%)'])
	df_share['1-10(d%)'] = df_share['1-10(%)']-_mean
	_text = _text + '1-10:{:.2f}% '.format(_mean)	
	_mean = np.median(df_share['11-50(%)'])
	df_share['11-50(d%)'] = df_share['11-50(%)']-_mean
	_text = _text + '11-50:{:.2f}% '.format(_mean)
	_mean = np.median(df_share['51-100(%)'])
	df_share['51-100(d%)'] = df_share['51-100(%)']-_mean
	_text = _text + '51-100:{:.2f}% '.format(_mean)
	_mean = np.median(df_share['101-200(%)'])
	df_share['101-200(d%)'] = df_share['101-200(%)']-_mean
	_text = _text + '101-200:{:.2f}% '.format(_mean)
	_mean = np.median(df_share['201-1000(%)'])
	df_share['201-1000(d%)'] = df_share['201-1000(%)']-_mean
	_text = _text + '201-1000:{:.2f}% '.format(_mean)
	_mean = np.median(df_share['1001-(%)'])
	df_share['1001-(d%)'] = df_share['1001-(%)']-_mean
	_text = _text + '1001-:{:.2f}% '.format(_mean)
	
	fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
	fig.suptitle(stock + '   ' + title, fontsize=24)
	plt.xticks(rotation=70)
	
	ax1_1 = ax1.twinx()
	
	DateList = df_share['Date'].values
	df_price_new = pd.DataFrame(columns=df_price.columns)
	for d in DateList:
		_new = df_price[df_price['Date']==d]
		if _new.empty == True:
			_new = df_price[df_price['Date']<d].tail(1)
		df_price_new = df_price_new.append(_new, ignore_index=True)
	df_price_new.reset_index(inplace=True)
	
	linestyle = ['--','-.',':','--','-.',':','--','-.',':','--','-.',':','--','-.',':','--','-.',':','--','-.',':','--','-.',':','--','-.',':']
	for col,lstyle in zip(df_share.columns, linestyle):
		if 'd%' not in col:
			continue
		if col == '1-10(d%)':
			lstyle = '-'
		ax1.plot(df_share['Date'], df_share[col], linestyle=lstyle, label=col)
	# draw grid
	ax1_1.plot(df_share['Date'], df_price_new['close'], label='close', color='black')
	ax1.legend(loc='upper left')
	ax1_1.legend(loc='upper right')
	ax1.grid()
	
	for col in df_share.columns:
		if col == 'Date':
			continue
		if df_share[col].dtypes == np.float64:
			df_share[col] = df_share[col] * 100
		df_share[col] = df_share[col].astype(int)
		df_share[col] = tanh_norm(df_share[col])
	print(df_share)	
	
	for col,lstyle in zip(df_share.columns, linestyle):
		if 'd%' in col:
			continue
		if '%' not in col:
			continue
		if col == '1-10(%)':
			lstyle = '-'
		ax2.plot(df_share['Date'], df_share[col], linestyle=lstyle, label=col)
	# draw grid
#	plt.xticks(rotation=70)
	ax1.text(0, 1.01, _text, transform=ax1.transAxes, fontsize=18)	
	ax2.legend(loc='upper left')
	ax2.grid()
	plt.savefig(pngName)
	
def draw_ROE(df_ROE, title, pngName):

	_year = range(2006, 2018)
	_roe = []
	for y in _year:
		col = str(y)+'ROE'
		_roe.append(df_ROE[col].values[0])
	df = pd.DataFrame(data={'年度': _year, 'ROE':_roe})

	bar_width = 0.8
	fig, ax0 = plt.subplots()
	ax0.bar(df['年度'], df['ROE'], bar_width,
			color='b',
            label='ROE')

	ax0.set_title(title)
	ax0.title.set_size(24)
	plt.xticks(df['年度'])
	
	min = df['ROE'].min()
	max = df['ROE'].max()
	_text = '股東權益報酬率 {:.1f} ~ {:.1f}'.format(min, max)	
	ax0.text(0, 1.01, _text, transform=ax0.transAxes, fontsize=18)
	ax0.legend(fontsize=16)
	ax0.grid()
	if pngName != None:
		plt.savefig(pngName)
	else:
		plt.show()		
		
def draw_ProfitMargin(df_gross, df_net, title, pngName, by12Q):

	xlabel = '季度' if by12Q == True else '年度'
	_col = []
	_gval = []
	_nval = []
	for c in df_gross.columns:
		if '平均毛利(%)' == c:
			continue
		if '毛利(%)' in c:
			c = c.rstrip('毛利(%)')
			_col.append(c)
			_gval.append(df_gross[c+'毛利(%)'].values[0])
			_nval.append(df_net[c+'淨利(%)'].values[0])
	
	df = pd.DataFrame(data={xlabel: _col, '毛利(%)':_gval, '淨利(%)':_nval})
	df.reset_index(inplace=True)
	bar_width = 0.35
	fig, ax0 = plt.subplots()
	ax0.bar(df.index-bar_width/2, df['毛利(%)'], bar_width,
			color='b',
            label='毛利(%)')
	ax0.bar(df.index+bar_width/2, df['淨利(%)'], bar_width,
			color='r',
            label='淨利(%)')
			
	ax0.set_title(title)
	ax0.title.set_size(24)
	plt.xticks(df.index, df[xlabel])
	
	min = df['毛利(%)'].min()
	max = df['毛利(%)'].max()
	_text = '毛利率 {:.1f} ~ {:.1f}'.format(min, max)	
	ax0.text(0, 1.01, _text, transform=ax0.transAxes, fontsize=18)

	min = df['淨利(%)'].min()
	max = df['淨利(%)'].max()
	_text = '淨利率 {:.1f} ~ {:.1f}'.format(min, max)	
	ax0.text(0, 1.05, _text, transform=ax0.transAxes, fontsize=18)

	ax0.legend(fontsize=16)
	ax0.grid()
	if pngName != None:
		plt.savefig(pngName)
	else:
		plt.show()		

		
def draw_oil_price(df_info, title, pngName):

	min = df_info['Price'].min()
	max = df_info['Price'].max()
	current = df_info['Price'].tail(1).values[0]
	currentDate = df_info['Date'].tail(1).values[0]
	_text = '歷史價格 {:.1f} ~ {:.1f}  目前 {} {:.1f}'.format(min, max, currentDate, current)

	bar_width = 1
	fig, ax0 = plt.subplots()
	ax0.bar(df_info.index, df_info['Price'], bar_width,
			color='b',
            label='原油價格')

	ax0.set_title(title)
	ax0.title.set_size(24)
	ax0.locator_params(axis='x', nbins=100)
	plt.xticks(df_info.index[::20], df_info[::20]['Date'], rotation=70)
	ax0.text(0, 1.01, _text, transform=ax0.transAxes, fontsize=18)
	ax0.legend(fontsize=16)
	ax0.grid()
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

	period = 2000

	df_div_all, _ = readDividenHistory('dividen.csv')
	df_ROE = readROEHistory('ROE_2006_2017.csv')
	df_gmargin = readGrossMarginProfit12Q()
	df_nmargin = readNetMarginProfit12Q()
	for stock in stockList:

		empty, df_main = readStockHistory(stock, period, raw=False)
		if empty == True:
			print('no data')
			continue
		(stock_id, stock_name) = stockList[stock]
		df_div = output_div(stock_id, df_main, df_div_all)

		stockPath = args['path'] + '/' + stock + '_' + stock_name
		os.makedirs(stockPath, exist_ok=True)
		pngName = stockPath+'/price_volume.png'
		draw = ta_draw(stock_id+'  '+stock_name, df_main, None, pngName)
		draw.draw_price_volume()		

		if True:
			# draw PER
			pngName = stockPath+'/PER.png'
			draw.draw_ta('PER', pngName)

			# draw MI_QFIIS
			pngName = stockPath+'/MI_QFIIS.png'
			draw.draw_ta('MI_QFIIS', pngName)

			# draw 3j
			pngName = stockPath+'/3j_foreign.png'
			draw.draw_ta('3j_foreign', pngName)		
			# draw 3j
			pngName = stockPath+'/3j_trust.png'
			draw.draw_ta('3j_trust', pngName)
			# draw 3j
			pngName = stockPath+'/3j_dealer.png'
			draw.draw_ta('3j_dealer', pngName)		
			
			# draw revenue
			pngName = stockPath+'/revenue.png'
			draw.draw_ta('revenue', pngName)

		for p in [240, 120, 60, 30]:
			df_short = df_main.tail(p)
			df_short.reset_index(drop=True, inplace=True)
			pngName = stockPath+'/price_volume_'+str(p)+'.png'
			draw = ta_draw(stock_id+'  '+stock_name, df_short, None, pngName)
			draw.draw_price_volume(str(p))
			if True:
				# draw MI_QFIIS
				pngName = stockPath+'/MI_QFIIS_'+str(p)+'.png'
				draw.draw_ta('MI_QFIIS', pngName)
				# draw 3j
				pngName = stockPath+'/3j_foreign_'+str(p)+'.png'
				draw.draw_ta('3j_foreign', pngName)
				# draw 3j
				pngName = stockPath+'/3j_trust_'+str(p)+'.png'
				draw.draw_ta('3j_trust', pngName)	
				# draw 3j
				pngName = stockPath+'/3j_dealer_'+str(p)+'.png'
				draw.draw_ta('3j_dealer', pngName)			
		
		if True:
			# draw EPS and dividen
			pngName = stockPath+'/EPS.png'
			draw_info_div(df_div, stock_id+'  '+stock_name + ' 股利', pngName)

			# draw ROE
			pngName = stockPath+'/ROE.png'
			draw_ROE(df_ROE[df_ROE['stock']==stock_id], stock_id+'  '+stock_name + ' 股東權益報酬率', pngName)
			
			# draw gross margin
			pngName = stockPath+'/margin_12Q.png'
			draw_ProfitMargin(	df_gmargin[df_gmargin['stock']==stock_id], 
								df_nmargin[df_nmargin['stock']==stock_id],
								stock_id+'  '+stock_name + ' 12季毛利率', pngName, True)
			# draw 股權分散表
			pngName = stockPath+'/share_holders.png'
			draw_share_holders(stock_id, df_main, u'股權分散表', pngName)

			# draw crude oil price
			pngName = stockPath+'/oil.png'
			df = pd.read_csv('history/crude_oil_price.csv')
			draw_oil_price(df, '原油價格', pngName)
		
if __name__ == '__main__':

	ap = argparse.ArgumentParser()
	ap.add_argument("-f", "--file", required=False, default='all_stock.csv')
	ap.add_argument("-s", "--stock", required=False, default='')
	ap.add_argument("-p", "--path", required=False, default=False, action='store_true')
	ap.add_argument("-d", "--debug", required=False, default=False, action='store_true')
	args = vars(ap.parse_args())

	main(args)