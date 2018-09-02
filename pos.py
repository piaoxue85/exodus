from __future__ import print_function

import numpy as np
import pandas as pd
from talib.abstract import *
import talib
import matplotlib.pyplot as plt
import matplotlib
import utility
from io import StringIO
import argparse

legal_man = [
				'1440美林', 
				'1520瑞士信貸',
				'9200凱基',
				'9800元大',
				'8880國泰綜合',
				'1380台灣匯立',
				'9600富邦',
				'1650瑞銀',
				'1360港麥格理',
				'1470台灣摩根',
				'1480美商高盛',
				'1530德意志',
				'1560港商野村',
				'1590花旗環球',
				'1650瑞銀',
				'8440摩根大通',
				'8840玉    山',
				'7790國票綜合',
				'9800元大',
				'9A00永豐金',
				'1040臺    銀',

			]

watch_list_9921 = [
				'965K富邦台中',
			]

watch_list_2436 = [
				'8152台新新莊',
			]

def pos_read(stock, _date):
	try:
		f = open('pos/'+stock+'_'+_date+'.csv', mode='r', encoding="utf-8")

		lines = f.readlines()
		new_lines = []
	
		new_lines.append(lines[2].split(',,')[0])
		del lines[0:3]
		for l in lines:
			for ll in l.replace('\u3000','').split(',,'):
				new_lines.append(ll)
		df = pd.read_csv(StringIO("\n".join(new_lines)), index_col=0)
	
		pos = pd.unique(df['券商'])
		price = pd.unique(df['價格'])
		col_pos = [	'券商', '買進', '賣出', '淨買入']
		col_price = [	'價格', '買進' ]
		df_pos_info = pd.DataFrame(columns=col_pos)
		df_price_distribute = pd.DataFrame(columns=col_price)
		for p in pos:
			df_pos = df[df['券商']==p]
			buy = df_pos['買進股數'].sum()/1000
			sell = df_pos['賣出股數'].sum()/1000
			if buy==0 and sell == 0:
				continue
			total = buy-sell
			_new = pd.DataFrame([[p, buy, sell, total]],columns=col_pos)
			df_pos_info = df_pos_info.append(_new, ignore_index=True)
			
		for p in price:
			df_price = df[df['價格']==p]
			buy = df_price['買進股數'].sum()/1000
			_new = pd.DataFrame([[p, buy]],columns=col_price)
			df_price_distribute = df_price_distribute.append(_new, ignore_index=True)	

		df_pos_info.reset_index(inplace=True)
		df_price_distribute.reset_index(inplace=True)

		return True, df_pos_info, df_price_distribute, df
	except:
		print('unable to process {} {}'.format(stock, _date))
		return False, None, None, None

def pos_update_stat(stock, _date, df_pos_info, df_price_distribute):
	try:
		df_pos_all = pd.read_csv('pos/'+stock+'.csv', index_col=0, delim_whitespace=False, header=0)
		for c in pd.unique(df_pos_info['券商']).tolist():
			if c not in df_pos_all.columns.tolist():
				df_pos_all[c] = pd.Series([float(0)]*len(df_pos_all), index=df_pos_all.index)
	except:
		col_pos = pd.unique(df_pos_info['券商']).tolist()
		col_pos.insert(0, 'Date')
		df_pos_all = pd.DataFrame(columns=col_pos)
	col_pos = df_pos_all.columns.tolist()
	pos = col_pos[1:]
	df_pos_info = df_pos_info.set_index('券商')
	vals = [df_pos_info.at[c, '淨買入'] if c in df_pos_info.index else 0 for c in pos]
	vals.insert(0, _date)
	_new = pd.DataFrame([vals],columns=col_pos)
	df_pos_all = df_pos_all.append(_new, ignore_index=True)
	df_pos_all.to_csv('pos/'+stock+'.csv', float_format='%.1f')
	return df_pos_all
	#for index, row in df.iterrows():

def pos_read_stat(stock):
	try:
		df_pos_all = pd.read_csv('pos/'+stock+'.csv', index_col=0, delim_whitespace=False, header=0)
		return True, df_pos_all
	except:
		return False, None

if __name__ == '__main__':

	ap = argparse.ArgumentParser()
	ap.add_argument("-s", "--stock", required=True, default='')
	ap.add_argument("-d", "--date", required=False, default='')
	ap.add_argument("-u", "--update", required=False, default=False, action='store_true')

	args = vars(ap.parse_args())
	if args['update'] == True:
		success, df_pos_info, df_price_distribute, df_orig  = pos_read(args['stock'], args['date'])
		if success == True:
			df_pos_all = pos_update_stat(args['stock'], args['date'], df_pos_info, df_price_distribute)

	if args['date'] != '':
		success, df_pos_info, df_price_distribute, df_orig  = pos_read(args['stock'], args['date'])
		if success == True:
			print('------- 買入大戶 ---------')
			df_pos_info=df_pos_info.sort_values(by=['淨買入'], ascending=False)
			print(df_pos_info[:5])
			print('------- 賣出大戶 ---------')
			df_pos_info=df_pos_info.sort_values(by=['淨買入'], ascending=True)
			print(df_pos_info[:5])
			print('------- 股價 ---------')
			df_price_distribute=df_price_distribute.sort_values(by=['買進'], ascending=False)			
			print(df_price_distribute[:5])

	empty, df_pos_all = pos_read_stat(args['stock'])
	total = 0
	print('------- 買入 ---------')
	for col in df_pos_all.columns:
		if col == 'Date':
			continue
		df_test = df_pos_all[df_pos_all[col] > 0]
		if df_test.empty == True:
			continue
		if len(df_test) == len(df_pos_all):
			print(col, ':', df_test[col].tolist())
	print('------- 賣出 ---------')
	for col in df_pos_all.columns:
		if col == 'Date':
			continue
		df_test = df_pos_all[df_pos_all[col] < 0]
		if df_test.empty == True:
			continue
		if len(df_test) == len(df_pos_all):
			print(col, ':', df_test[col].tolist())
		#total += df_test[col].sum()

	period = 4 if len(df_pos_all) >=4 else len(df_pos_all)
	print('------- 轉買為賣 ---------')
	for col in df_pos_all.columns:
		if col == 'Date':
			continue
		vals = df_pos_all[col].tail(period).values

		pick = all(number>0 for number in vals[0:period-1])
		if pick == True and vals[period-1] < 0:
			print(col, ':', vals)

	print('------- 轉賣為買 ---------')
	for col in df_pos_all.columns:
		if col == 'Date':
			continue
		vals = df_pos_all[col].tail(period).values

		pick = all(number<0 for number in vals[0:period-1])
		if pick == True and vals[period-1] > 0:
			print(col, ':', vals)

	print('------- 法人 ---------')
	for col in legal_man:
		try:
			print(col, '({:.1f}):'.format(df_pos_all[col].sum()), df_pos_all[col].values)
		except:
			continue


	print('------- 注意 ---------')
	if args['stock'] == '9921':
		watch = watch_list_9921
	if args['stock'] == '2436':
		watch = watch_list_2436
	try:
		for col in watch:
			try:
				print(col, '({:.1f}):'.format(df_pos_all[col].sum()), df_pos_all[col].values)
			except:
				continue
	except:
		print('')
#print(df_test)

