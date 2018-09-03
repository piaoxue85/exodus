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
import json
import os

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
	if int(_date) not in df_pos_all['Date'].values.tolist():
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

def df2html(df, title, fhtml):
	print("<h2 align=\"left\" style=\"color:blue;\">{}</h2>\n".format(title), file=fhtml)
	print(tblHdr, file=fhtml)
	print('<tr>', file=fhtml)
	for col in df.columns:
		print('<th align=\"left\">{}</th>\n'.format(col), file=fhtml)
	print('</tr>', file=fhtml)

	
	for index, row in df.iterrows():
		#print('<td align=\"left\">{:.2f}</td>'.format(val), file=fhtml)
		print('<tr>', file=fhtml)
		for val in row.values:
			if type(val) is float:
				print('<td align=\"left\">{:.2f}</td>'.format(val), file=fhtml)
			else:
				print('<td align=\"left\">{}</td>'.format(val), file=fhtml)
		print('</tr>', file=fhtml)		
	print(tblEnd, file=fhtml)


if __name__ == '__main__':

	ap = argparse.ArgumentParser()
	ap.add_argument("-s", "--stock", required=True, default='')
	ap.add_argument("-d", "--date", required=False, default='')
	ap.add_argument("-u", "--update", required=False, default=False, action='store_true')
	ap.add_argument("-p", "--point", required=False, default='')
	ap.add_argument("-o", "--outpath", required=False, default='')
	ap.add_argument("-n", "--name", required=False, default='')
	args = vars(ap.parse_args())

	fList = [f for f in os.listdir('pos') if args['stock']+'_' in f]


	legal_man = json.load(open('pos/legal_man.json'))
	watch = json.load(open('pos/watch.json'))	

	htmlHdr = '<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<title>{}</title>\n\t\t<meta charset=\"UTF-8\">\n\t</head>'.format(args['stock'])
	htmlTail = """</html>"""
	_bodyBegin = """
	<body>
	"""
	_bodyEnd = """
	</body>
	"""
	_style = """
	<style>
		table, th, td {
		border: 1px solid black;
	}
	</style>	
	"""
	tblHdr = """<table style="width:50%">"""
	tblEnd = """</table>"""
	_space = '&nbsp&nbsp&nbsp&nbsp&nbsp'

	name = args['name'] if 'name' in args else ''
	if args['outpath'] != '':
		fhtml = open(args['outpath'], 'w')
		print(htmlHdr, file=fhtml)
		print(_style, file=fhtml)
		print(_bodyBegin, file=fhtml)
		_title = "<h1 align=\"center\" style=\"color:blue;\">{}</h1>\n".format(name)	
		print(_title, file=fhtml)

	if args['update'] == True:
		success, df_pos_info, df_price_distribute, df_orig  = pos_read(args['stock'], args['date'])
		if success == True:
			df_pos_all = pos_update_stat(args['stock'], args['date'], df_pos_info, df_price_distribute)

	if args['date'] != '':
		success, df_pos_info, df_price_distribute, df_orig  = pos_read(args['stock'], args['date'])
		if success == True:

			df_pos_info=df_pos_info.sort_values(by=['淨買入'], ascending=False)
			print('------- 買入大戶 ---------')
			print(df_pos_info[:5])
			if args['outpath'] != '':
				df2html(df_pos_info[:10], '買入大戶', fhtml)
			print('------- 賣出大戶 ---------')
			df_pos_info=df_pos_info.sort_values(by=['淨買入'], ascending=True)
			print(df_pos_info[:5])
			if args['outpath'] != '':
				df2html(df_pos_info[:10], '賣出大戶', fhtml)
			print('------- 股價 ---------')
			df_price_distribute=df_price_distribute.sort_values(by=['買進'], ascending=False)			
			print(df_price_distribute[:5])
			if args['outpath'] != '':
				df2html(df_price_distribute[:5], '股價', fhtml)

	empty, df_pos_all = pos_read_stat(args['stock'])
	total = 0
	print('------- 買入 ---------')
	if args['outpath'] != '':
		print("<h2 align=\"left\" style=\"color:blue;\">{}</h2>\n".format('連續買入'), file=fhtml)
	for col in df_pos_all.columns:
		if col == 'Date':
			continue
		df_test = df_pos_all[df_pos_all[col] > 0]
		if df_test.empty == True:
			continue
		if len(df_test) == len(df_pos_all):
			print(col, ':', df_test[col].tolist())
			if args['outpath'] != '':
				print('\t<p>{}({})<b><font color=\"red\">{}</b>{}</font></p>'.format(col, int(df_test[col].sum()),_space, df_test[col].tolist()), file=fhtml)

	print('------- 賣出 ---------')
	if args['outpath'] != '':
		print("<h2 align=\"left\" style=\"color:blue;\">{}</h2>\n".format('連續賣出'), file=fhtml)

	for col in df_pos_all.columns:
		if col == 'Date':
			continue
		df_test = df_pos_all[df_pos_all[col] < 0]
		if df_test.empty == True:
			continue
		if len(df_test) == len(df_pos_all):
			print(col, ':', df_test[col].tolist())
			if args['outpath'] != '':
				print('\t<p>{}({})<b><font color=\"red\">{}</b>{}</font></p>'.format(col, int(df_test[col].sum()),_space, df_test[col].tolist()), file=fhtml)

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

	print('------- 外資法人 ---------')
	for col in legal_man['foreigner']:
		try:
			print(col, '({:.1f}):'.format(df_pos_all[col].sum()), df_pos_all[col].values)
		except:
			continue

	print('------- 投信自營商 ---------')
	for col in legal_man['trust']:
		try:
			print(col, '({:.1f}):'.format(df_pos_all[col].sum()), df_pos_all[col].values)
		except:
			continue



	try:

		watch = watch[args['stock']]
		print('------- 注意 ---------')	
		for col in watch:
			try:
				print(col, '({:.1f}):'.format(df_pos_all[col].sum()), df_pos_all[col].values)
			except:
				continue
	except:
		print('')

	if args['point'] != '':
		remain = 0
		for f in fList:
			avgbuy = 0
			avgsell = 0
			_date = f.lstrip(args['stock']).lstrip('_').rstrip('.csv')
			print('*****', _date)
			success, df_pos_info, df_price_distribute, df_orig  = pos_read(args['stock'], _date)
			
			if success == True:
				df = df_orig[df_orig['券商'].str.contains(args['point'])]
				try:
					remain += (df['買進股數'].sum()-df['賣出股數'].sum())/1000
				except:
					remain += 0
				#print(df)
				total_sell = 0
				total_buy = 0
				df['total_buy'] = df['買進股數'] * df['價格']
				df['total_sell'] = df['賣出股數'] * df['價格']
				#for index, row in df.iterrows():
				#	if row['買進股數'] != 0:
				#		total_buy = row['買進股數'] * 
				#print(df)
				print('買進: {:.1f} 成本 {:.1f}'.format(df['total_buy'].sum()/1000, df['total_buy'].sum()/df['買進股數'].sum()))
				print('賣出: {:.1f} 成本 {:.1f}'.format(df['total_sell'].sum()/1000, df['total_sell'].sum()/df['賣出股數'].sum()))
				print('持有:', remain)

	if args['outpath'] != '':
		fhtml.close()
#print(df_test)

