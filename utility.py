from __future__ import print_function

import numpy as np
import pandas as pd
from ta_predict import *
from collections import OrderedDict
import requests
from io import StringIO
from datetime import date, datetime, timedelta
import datetime as dt
import time
import json
import os
from googlefinance.client import get_price_data, get_prices_data, get_prices_time_data

def tanh_norm(x):
	u = np.mean(x)
	o = np.std(x)
	
	r = 0.01*(x.values-u)
	r = r/o+1
	r = 0.5*np.tanh(r)
	r = pd.Series(r, x.index)
	return r
	
def min_max_norm(scaler, df_data):
	_data = np.reshape(df_data.values, (-1, 1))
	_data = scaler.fit_transform(_data)
	_data = np.reshape(_data, (1, -1))
	return pd.Series(_data[0], df_data.index)

def readStockList(fname):
	_stock = OrderedDict()
	f = open(fname, mode='r', encoding="utf-8")
	for line in f:
		w = line.replace('\n', '').split(',')
		_stock[w[0]] = (w[0], w[1])
	f.close()
	return OrderedDict(sorted(_stock.items()))
	#return _stock

def writeStockList(fname, stockDict):
	_stock = dict()
	f = open(fname, mode='w', encoding="utf-8")
	for stock in stockDict:
		(id, name) = stockDict[stock]
		f.write('{},{}\n'.format(id, name))
	f.close()

def update_stock_history(stock, period):
	param = {
	    'q': stock, 		# Stock symbol (ex: "AAPL")
	    'i': "86400", 		# Interval size in seconds ("86400" = 1 day intervals)
	    #'i': "300", 		# Interval size in seconds ("86400" = 1 day intervals)
	    'x': "TPE", 		# Stock exchange symbol on which stock is traded (ex: "NASD")
	    'p': period 			# Period (Ex: "1Y" = 1 year)
	}

	df = get_price_data(param)
	return df

def daterange(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + timedelta(n)

def update_daily_per(year, month, day, writFile=False):
	datestr = '{}{:02d}{:02d}'.format(year, month, day)
	try:
		r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL')
		df = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
						for i in r.text.split('\n') if len(i.split('",')) == 17 and i[0] != '='])), header=0)
		if writFile == True:
			df.to_csv('history/per/'+datestr+'.csv')
		return (True, df)
	except:
		print('unable to get ', datestr)
		return (False, None)

def update_daily_3j(year, month, day, writFile=False):
	datestr = '{}{:02d}{:02d}'.format(year, month, day)
	try:
		_str = 'http://www.twse.com.tw/fund/T86?response=csv&date=' + datestr + '&selectType=ALLBUT0999'
		r = requests.post(_str)
		df = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
						for i in r.text.split('\n') if len(i.split('",')) == 20 and i[0] != '='])), header=0)
		if writFile == True:
			df.to_csv('history/3j/'+datestr+'.csv')
		return (True, df)
	except:
		print('unable to get ', datestr)
		return (False, None)

def update_daily_3j_period(startDate, period):
	years = 0
	months = 0
	days = 0
	endDate = startDate
	if 'Y' in period:
		years = int(period.rstrip('Y'))
		endDate = endDate.replace(year=endDate.year + years)
	if 'M' in period:
		months = int(period.rstrip('M'))
		years = endDate.year+int((months + endDate.month) / 12)
		months = (months + endDate.month) % 12 
		endDate = endDate.replace(month=months)
		endDate = endDate.replace(year=years)
	if 'd' in period:
		days = int(period.rstrip('d'))
		endDate = endDate + timedelta(days=days)

	for single_date in daterange(startDate, endDate):
		datestr = '{}{:02d}{:02d}'.format(single_date.year, single_date.month, single_date.day)
		print('update 3j ', datestr)
		update_daily_3j(single_date.year, single_date.month, single_date.day, writFile=True)
		time.sleep(10)


def readPolicy(path):
	json_data=open(path)
	policy = json.load(json_data)
	return policy		
		
def update_daily_per_period(startDate, period):
	years = 0
	months = 0
	days = 0
	endDate = startDate
	if 'Y' in period:
		years = int(period.rstrip('Y'))
		endDate = endDate.replace(year=endDate.year + years)
	if 'M' in period:
		months = int(period.rstrip('M'))
		years = endDate.year+int((months + endDate.month) / 12)
		months = (months + endDate.month) % 12 
		endDate = endDate.replace(month=months)
		endDate = endDate.replace(year=years)
	if 'd' in period:
		days = int(period.rstrip('d'))
		endDate = endDate + timedelta(days=days)

	for single_date in daterange(startDate, endDate):
		datestr = '{}{:02d}{:02d}'.format(single_date.year, single_date.month, single_date.day)
		print('update ', datestr)
		update_daily_per(single_date.year, single_date.month, single_date.day, writFile=True)
		time.sleep(10)
		#print(datestr)
	#r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL')
	#df = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
					#for i in r.text.split('\n') if len(i.split('",')) == 17 and i[0] != '='])), header=0)
	#df.to_csv('history/per/'+datestr+'.csv')

def update_daily(startDate, period):
	years = 0
	months = 0
	days = 0
	endDate = startDate
	if 'Y' in period:
		years = int(period.rstrip('Y'))
		endDate = endDate.replace(year=endDate.year + years)
	if 'M' in period:
		months = int(period.rstrip('M'))
		years = endDate.year+int((months + endDate.month) / 12)
		months = (months + endDate.month) % 12 
		endDate = endDate.replace(month=months)
		endDate = endDate.replace(year=years)
	if 'd' in period:
		days = int(period.rstrip('d'))
		endDate = endDate + timedelta(days=days)

	for single_date in daterange(startDate, endDate):
		datestr = '{}{:02d}{:02d}'.format(single_date.year, single_date.month, single_date.day)
		print('update ', datestr)
		(got_data, df) = update_daily_per(single_date.year, single_date.month, single_date.day, writFile=False)
		if got_data == False:
			continue
		for index, row in df.iterrows():
			stock = row['證券代號']
			path = 'history/'+row['證券代號']+'.csv'
			if os.path.exists(path) == False:
				print('		no {} history file'.format(path))
				continue
			#f = open(fname, mode='a', encoding="utf-8")
			try:
				df_stock = pd.read_csv(path)
				mydatetime = datetime.combine(single_date, dt.time(13,30))
				revenue = get_monthly_revenus(stock, single_date.year, single_date.month)
				volume = float(row['成交股數'].replace(',', ''))/1000
				PER = float(row['本益比'])
				_open = float(row['開盤價'])
				_close = float(row['收盤價'])
				high = float(row['最高價'])
				low = float(row['最低價'])
				dateStr = mydatetime.strftime('%Y-%m-%d')
				new_sample = '{},{},{},{},{},{},{},{},{},{},{}\n'.format(len(df_stock), 
												_open, high, low, _close, volume, 
												mydatetime,
												dateStr,
												0,
												revenue,
												PER)
				if len(df_stock[df_stock['DateStr'] == dateStr]) > 0:
					print('		skip overwrite')
				else:
					print('		update ', stock, new_sample)
					f = open(path, mode='a', encoding="utf-8")
					f.write(new_sample)
					f.close()

			except:
				print('		data error', stock)
		time.sleep(10)
		
def get_daily_per(stock, year, month, day):
	datestr = '{}{:02d}{:02d}'.format(year, month, day)
	try:
	#if True:
		df = pd.read_csv('history/per/'+datestr+'.csv')
		if df.empty == True:
			return 0
		
		df.rename(columns={'本益比': 'PER', '證券代號': 'stock'}, inplace=True)					
		df['stock'] = df['stock'].astype(str)

		per = df['PER'].loc[df['stock']==stock]
		per = float(per.values[0])
		return per
	except:
		print('Can not get {} {}'.format(stock, datestr))
		return 0
		
_last_read_revenue_date = None		
_last_reven_df = None
def get_monthly_revenus(stock, year, month):
	global _last_read_revenue_date, _last_reven_df
	year = year-1911
	datestr = '{}_{}'.format(year, month)
	try:
		if _last_read_revenue_date == datestr:
			df = _last_reven_df
		else:
			df = pd.read_csv('history/revenue/'+datestr+'.csv')
			if df.empty != True:
				df.rename(columns={'當月營收': 'revenue', '公司代號': 'stock'}, inplace=True)					
				df['stock'] = df['stock'].astype(str)
			_last_reven_df = df
			_last_read_revenue_date = datestr

		if df.empty == True:
			return 0

		revenue = df['revenue'].loc[df['stock']==stock]
		revenue = float(revenue.values[0])
		return revenue
	except:
		return 0		
		
def readStockHistory(stock, period, raw=True):
	try:
		df_main = pd.read_csv('history/'+stock+'.csv', dtype={'volume':np.float64}, delim_whitespace=False, header=0)
	except:
		print('history/'+stock+'.csv has problem')
		return True, None
		
	if df_main.empty:
		return True, None

	df_main = df_main.dropna()
	df_main['Date'] = pd.to_datetime(df_main.Date)
	df_main['DateStr'] = df_main['Date'].dt.strftime('%Y-%m-%d')
	
	if 'Open' in df_main.columns.values:
		#df_main['Volume'] = df_main['Volume'] / 1000
		df_main.rename(columns={'Open': 'open', 'Close': 'close', \
							'High': 'high', 'Low': 'low', 'Volume': 'volume'
							}, inplace=True)
		
	if raw == False:
		df_main['k'], df_main['d'] = talib.STOCH(df_main['high'], df_main['low'], df_main['close'], fastk_period=9)
		df_main['RSI'] = talib.RSI(df_main['close'], timeperiod=10)
		df_main['macd'], df_main['macdsignal'], df_main['macdhist'] = talib.MACD(df_main['close'])
		df_main['SMA'] = talib.SMA(df_main['close'])
		df_main['BIAS'] = ((df_main['close']-df_main['SMA'])/df_main['close']) * 100
	if 'eps' not in df_main.columns.values.tolist():
		df_main['eps'] = pd.Series([float(0)]*len(df_main), df_main.index)		
	if 'revenue' not in df_main.columns.values.tolist():
		df_main['revenue'] = pd.Series([float(0)]*len(df_main), df_main.index)
	if 'PER' not in df_main.columns.values.tolist():
		df_main['PER'] = pd.Series([float(0)]*len(df_main), df_main.index)
	df_main = df_main.dropna()
	total = len(df_main)
	if (total > period):
		df_main = df_main[total-period:]	

	df_main.reset_index(drop=True, inplace=True)
	
	return False, df_main
	

def update_monthly_report(year, month):
    
	print('Get vol {} {}'.format(year, month))
	# 假如是西元，轉成民國
	if year > 1990:
		year -= 1911

	url = 'http://mops.twse.com.tw/nas/t21/sii/t21sc03_'+str(year)+'_'+str(month)+'_0.html'
	if year <= 98:
		url = 'http://mops.twse.com.tw/nas/t21/sii/t21sc03_'+str(year)+'_'+str(month)+'.html'

	# 偽瀏覽器
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

	# 下載該年月的網站，並用pandas轉換成 dataframe
	try:
		r = requests.get(url, headers=headers)
		r.encoding = 'big5'
		html_df = pd.read_html(StringIO(r.text))
	except:
		return

	# 處理一下資料
	if html_df[0].shape[0] > 500:
		df = html_df[0].copy()
	else:
		df = pd.concat([df for df in html_df if df.shape[1] <= 11])
	df = df[list(range(0,10))]
	column_index = df.index[(df[0] == '公司代號')][0]
	df.columns = df.iloc[column_index]
	df['當月營收'] = pd.to_numeric(df['當月營收'], 'coerce')
	df = df[~df['當月營收'].isnull()]
	df = df[df['公司代號'] != '合計']

	#print(df)
	df.to_csv('history/revenue/{}_{}'.format(year, month)+'.csv')
	
	# 偽停頓
	time.sleep(30)
	#return df

def financial_statement(year, season, type='綜合損益彙總表'):
	if year >= 1000:
		year -= 1911

	if type == '綜合損益彙總表':
		url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb04'
	elif type == '資產負債彙總表':
		url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb05'
	elif type == '營益分析彙總表':
		url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb06'
	else:
		print('type does not match')
	
	r = requests.post(url, {
					'encodeURIComponent':1,
					'step':1,
					'firstin':1,
					'off':1,
					'TYPEK':'sii',
					'year':str(year),
					'season':str(season),
					})

	r.encoding = 'utf8'
	dfs = pd.read_html(r.text)


	for i, df in enumerate(dfs):
		df.columns = df.iloc[0]
		dfs[i] = df.iloc[1:]

	df = pd.concat(dfs).applymap(lambda x: x if x != '--' else np.nan)
	df = df[df['公司代號'] != '公司代號']
	df = df[~df['公司代號'].isnull()]
	return df

def readROEHistory(fname):
	df = pd.read_csv('history/'+fname, delim_whitespace=False, header=0)
	df.rename(columns={'排名': 'ranking', '代號': 'stock', \
							'名稱': 'name', 
							'平均ROE(%)': 'avg_ROE', 
							'2006ROE(%)': '2006ROE',
							'2007ROE(%)': '2007ROE',
							'2008ROE(%)': '2008ROE',
							'2009ROE(%)': '2009ROE',
							'2010ROE(%)': '2010ROE',
							'2011ROE(%)': '2011ROE',
							'2012ROE(%)': '2012ROE',
							'2013ROE(%)': '2013ROE',
							'2014ROE(%)': '2014ROE',
							'2015ROE(%)': '2015ROE',
							'2016ROE(%)': '2016ROE',
							'2017ROE(%)': '2017ROE',
							}, inplace=True)

	df=df.drop(columns=[u'成交', u'漲跌價', u'漲跌幅', u'18Q1ROE(%)'])
	df['std_ROE']=df.std(axis=1, ddof=0)
	#print(df)
	
	df=df.sort_values(by=['avg_ROE'], ascending=False)
	df.reset_index(inplace=True)
	df=df[['stock', 'name', 'ranking', 'avg_ROE', 'std_ROE', \
					'2017ROE', '2016ROE', '2015ROE', '2014ROE', '2013ROE', \
					'2012ROE', '2011ROE', '2010ROE', '2009ROE', '2008ROE', \
					'2007ROE', '2006ROE']]
	df['stock']=df['stock'].str.replace('=', '')
	df['stock']=df['stock'].str.replace('"', '')
	return df
	
def translateFinacialHistory():
	divident_list = [	('dividen_2006.csv', '2006'), 
						('dividen_2007.csv', '2007'),
						('dividen_2008.csv', '2008'),
						('dividen_2009.csv', '2009'),
						('dividen_2010.csv', '2010'),
						('dividen_2011.csv', '2011'),
						('dividen_2012.csv', '2012'),
						('dividen_2013.csv', '2013'),
						('dividen_2014.csv', '2014'),
						('dividen_2015.csv', '2015'),
						('dividen_2016.csv', '2016'),
						('dividen_2017.csv', '2017'),
						('dividen_2018.csv', '2018'),]
						#('finacial_2006.csv', '2006'),
						#('finacial_2007.csv', '2007'),
						#('finacial_2008.csv', '2008'),
						#('finacial_2009.csv', '2009'),
						#('finacial_2010.csv', '2010'),
						#('finacial_2011.csv', '2011'),
						#('finacial_2012.csv', '2012'),
						#('finacial_2013.csv', '2013'),
						#('finacial_2014.csv', '2014'),
						#('finacial_2015.csv', '2015'),
						#('finacial_2016.csv', '2016'),
						#('finacial_2017.csv', '2017'),
						#]
						
	df_finacial = pd.DataFrame(columns=[	'stock', 'name',
								'div_2006_cash', 'div_2007_cash', 'div_2008_cash', 'div_2009_cash',
								'div_2010_cash', 'div_2011_cash', 'div_2012_cash', 'div_2013_cash',
								'div_2014_cash', 'div_2015_cash', 'div_2016_cash', 'div_2017_cash', 'div_2018_cash',
								'div_2006_stock', 'div_2007_stock', 'div_2008_stock', 'div_2009_stock',
								'div_2010_stock', 'div_2011_stock', 'div_2012_stock', 'div_2013_stock',
								'div_2014_stock', 'div_2015_stock', 'div_2016_stock', 'div_2017_stock', 'div_2018_stock',
								'div_2006_all', 'div_2007_all', 'div_2008_all', 'div_2009_all',
								'div_2010_all', 'div_2011_all', 'div_2012_all', 'div_2013_all',
								'div_2014_all', 'div_2015_all', 'div_2016_all', 'div_2017_all', 'div_2018_all',
								'payout_ratio_2006', 'yield_2006', 
								'payout_ratio_2007', 'yield_2007',
								'payout_ratio_2008', 'yield_2008',
								'payout_ratio_2009', 'yield_2009',
								'payout_ratio_2010', 'yield_2010',
								'payout_ratio_2011', 'yield_2011',
								'payout_ratio_2012', 'yield_2012',
								'payout_ratio_2013', 'yield_2013',
								'payout_ratio_2014', 'yield_2014',
								'payout_ratio_2015', 'yield_2015',
								'payout_ratio_2016', 'yield_2016',
								'payout_ratio_2017', 'yield_2017',
								'payout_ratio_2018', 'yield_2018',])
	for (f, _year) in divident_list:
		df = pd.read_csv('history/'+f)
		df['代號']=df['代號'].str.replace('=', '')
		df['代號']=df['代號'].str.replace('"', '')	

		df.rename(columns={'代號': 'stock', '名稱': 'name', '股利發放年度': 'year'}, inplace=True)		
		for index, row in df.iterrows():
			stock = row['stock']
			name = row['name']
			year = row['year']
			if year == '-':
				year = _year
			div_cash = row['現金股利']
			div_stock = row['股票股利']
			div_all = row['合計股利']
			_yield = row['合計殖利率']
			_ratio = row['盈餘總分配率']
			#year = row['year']
			print('stock = {} {} {}'.format(f, stock, year))
			if stock not in df_finacial['stock'].values:
				_new = pd.DataFrame([[stock, name]],columns=[	'stock', 'name'])
				df_finacial = df_finacial.append(_new, ignore_index=True)
			new_row = df_finacial.loc[df_finacial['stock']==stock]
			new_row['div_2006']=100
			if f == 'dividen_2018.csv':
				year = '2018'
			elif year == '2018':
				continue
			column = 'div_'+year

			df_finacial['div_'+year+'_cash'].loc[df_finacial['stock']==stock] = div_cash
			df_finacial['div_'+year+'_stock'].loc[df_finacial['stock']==stock] = div_stock
			df_finacial['div_'+year+'_all'].loc[df_finacial['stock']==stock] = div_all
			df_finacial['yield_'+year].loc[df_finacial['stock']==stock] = _yield
			df_finacial['payout_ratio_'+year].loc[df_finacial['stock']==stock] = _ratio
		#break
	return df_finacial

__df_div_cache = pd.DataFrame() 
__df_div_cache_year = '0000'
def readDividenByStockYear(year, stock):
	global __df_div_cache, __df_div_cache_year
	if __df_div_cache.empty == False and __df_div_cache_year == year and stock in __df_div_cache['stock'].values:
		return __df_div_cache

	df = pd.read_csv('history/dividen_'+str(year)+'.csv', dtype={'股利發放年度':str})
	df.rename(columns={	'代號': 'stock', 
						'名稱': 'name', 
						'股利發放年度': 'year', 
						'現金股利': 'div_cash',
						'股票股利': 'div_stock',
						'除息交易日': 'div_cash_date',
						'除權交易日': 'div_stock_date',
						}, inplace=True)
	df['stock'] = df['stock'].str.replace('=', '')
	df['stock'] = df['stock'].str.replace('"', '')

	df = df[df['stock']==stock]
	try:
		df = df[df['year']==year]
	except:
		print('error')
	df['div_cash'].fillna(0)
	df['div_stock'].fillna(0)
	for index, row in df.iterrows():
		try:
			_dateStr = row['div_cash_date']
			_dateStr = '20'+_dateStr.split('\'')[0]+'-'+_dateStr.split('\'')[1].split('/')[0]+'-'+_dateStr.split('\'')[1].split('/')[1]
		except:
			_dateStr = '0000-0-0'
		df.loc[index, 'div_cash_date'] = _dateStr
		try:
			_dateStr = row['div_stock_date']
			_dateStr = '20'+_dateStr.split('\'')[0]+'-'+_dateStr.split('\'')[1].split('/')[0]+'-'+_dateStr.split('\'')[1].split('/')[1]
		except:
			_dateStr = '0000-0-0'
		df.loc[index, 'div_stock_date'] = _dateStr

	__df_div_cache = df
	__df_div_cache_year = year
	return df

def translateDividenHistory(outfile):
	divident_list = [	('dividen_2006.csv', '2006'), 
						('dividen_2007.csv', '2007'),
						('dividen_2008.csv', '2008'),
						('dividen_2009.csv', '2009'),
						('dividen_2010.csv', '2010'),
						('dividen_2011.csv', '2011'),
						('dividen_2012.csv', '2012'),
						('dividen_2013.csv', '2013'),
						('dividen_2014.csv', '2014'),
						('dividen_2015.csv', '2015'),
						('dividen_2016.csv', '2016'),
						('dividen_2017.csv', '2017'),
						('dividen_2018.csv', '2018'),
						]

	df_div = pd.DataFrame(columns=[	'stock', 'name',
								'div_2006_cash', 'div_2007_cash', 'div_2008_cash', 'div_2009_cash',
								'div_2010_cash', 'div_2011_cash', 'div_2012_cash', 'div_2013_cash',
								'div_2014_cash', 'div_2015_cash', 'div_2016_cash', 'div_2017_cash', 'div_2018_cash',
								'div_2006_stock', 'div_2007_stock', 'div_2008_stock', 'div_2009_stock',
								'div_2010_stock', 'div_2011_stock', 'div_2012_stock', 'div_2013_stock',
								'div_2014_stock', 'div_2015_stock', 'div_2016_stock', 'div_2017_stock', 'div_2018_stock',
								'div_2006_all', 'div_2007_all', 'div_2008_all', 'div_2009_all',
								'div_2010_all', 'div_2011_all', 'div_2012_all', 'div_2013_all',
								'div_2014_all', 'div_2015_all', 'div_2016_all', 'div_2017_all', 'div_2018_all',
								'payout_ratio_2006', 'yield_2006', 
								'payout_ratio_2007', 'yield_2007',
								'payout_ratio_2008', 'yield_2008',
								'payout_ratio_2009', 'yield_2009',
								'payout_ratio_2010', 'yield_2010',
								'payout_ratio_2011', 'yield_2011',
								'payout_ratio_2012', 'yield_2012',
								'payout_ratio_2013', 'yield_2013',
								'payout_ratio_2014', 'yield_2014',
								'payout_ratio_2015', 'yield_2015',
								'payout_ratio_2016', 'yield_2016',
								'payout_ratio_2017', 'yield_2017',
								'payout_ratio_2018', 'yield_2018',
 								'eps_2006', 'eps_2007', 'eps_2008', 'eps_2009', 'eps_2010', 'eps_2011',
								'eps_2012', 'eps_2013', 'eps_2014', 'eps_2015', 'eps_2016', 'eps_2017',
								'eps_2018'
								])
	for (f, _year) in divident_list:
		df_orig = pd.read_csv('history/'+f)
		df_orig['代號']=df_orig['代號'].str.replace('=', '')
		df_orig['代號']=df_orig['代號'].str.replace('"', '')	

		df_orig.rename(columns={'代號': 'stock', '名稱': 'name', '股利發放年度': 'year'}, inplace=True)		
		for index, row in df_orig.iterrows():
			stock = row['stock']
			name = row['name']
			year = row['year']
			if year == '-':
				year = _year
			div_cash = row['現金股利']
			div_stock = row['股票股利']
			div_all = row['合計股利']
			_yield = row['合計殖利率']
			_ratio = row['盈餘總分配率']
			#year = row['year']
			print('stock = {} {} {}'.format(f, stock, year))
			if stock not in df_div['stock'].values:
				_new = pd.DataFrame([[stock, name]],columns=[	'stock', 'name'])
				df_div = df_div.append(_new, ignore_index=True)

			if f == 'dividen_2018.csv':
				year = '2018'
			elif year == '2018':
				continue

			df_div['div_'+year+'_cash'].loc[df_div['stock']==stock] = div_cash
			df_div['div_'+year+'_stock'].loc[df_div['stock']==stock] = div_stock
			df_div['div_'+year+'_all'].loc[df_div['stock']==stock] = div_all
			df_div['yield_'+year].loc[df_div['stock']==stock] = _yield
			df_div['payout_ratio_'+year].loc[df_div['stock']==stock] = _ratio
			df_div['eps_'+year].loc[df_div['stock']==stock] = row['所屬EPS']
		#break
	df_div.fillna(0, inplace=True)
	df_div['std_yield']=pd.Series([float(0)]*len(df_div), df_div.index)
	df_div['std_payout']=pd.Series([float(0)]*len(df_div), df_div.index)
	df_div['mean_yield']=pd.Series([float(0)]*len(df_div), df_div.index)
	df_div['mean_payout']=pd.Series([float(0)]*len(df_div), df_div.index)

	for index, row in df_div.iterrows():
		_yield = [	row['yield_2006'],
					row['yield_2007'],
					row['yield_2008'],
					row['yield_2009'],
					row['yield_2010'],
					row['yield_2011'],
					row['yield_2011'],
					row['yield_2012'],
					row['yield_2013'],
					row['yield_2014'],
					row['yield_2015'],
					row['yield_2016'],
					row['yield_2017']]
		df_div.loc[index, 'std_yield'] = np.std(_yield)
		df_div.loc[index, 'mean_yield'] = np.mean(_yield)
		_payout = [	row['payout_ratio_2006'],
					row['payout_ratio_2007'],
					row['payout_ratio_2008'],
					row['payout_ratio_2009'],
					row['payout_ratio_2010'],
					row['payout_ratio_2011'],
					row['payout_ratio_2011'],
					row['payout_ratio_2012'],
					row['payout_ratio_2013'],
					row['payout_ratio_2014'],
					row['payout_ratio_2015'],
					row['payout_ratio_2016'],
					row['payout_ratio_2017']]
		df_div.loc[index, 'std_payout'] = np.std(_payout)
		df_div.loc[index, 'mean_payout'] = np.mean(_payout)

		_div_all = [	row['div_2006_all'],
					row['div_2006_all'],
					row['div_2007_all'],
					row['div_2008_all'],
					row['div_2009_all'],
					row['div_2010_all'],
					row['div_2011_all'],
					row['div_2012_all'],
					row['div_2013_all'],
					row['div_2014_all'],
					row['div_2015_all'],
					row['div_2016_all'],
					row['div_2017_all']]
		df_div.loc[index, 'std_div_all'] = np.std(_div_all)
		df_div.loc[index, 'mean_div_all'] = np.mean(_div_all)

	df_div=df_div.sort_values(by=['mean_div_all'], ascending=False)
	df_div.reset_index(inplace=True)
	df_div = df_div[['stock', 'name', 
					'mean_div_all', 'std_div_all',
					'mean_yield', 'std_yield', 'mean_payout', 'std_payout',
					'eps_2018', 'yield_2018', 'payout_ratio_2018', 'div_2018_all', 'div_2018_cash', 'div_2018_stock',
					'eps_2017', 'yield_2017', 'payout_ratio_2017', 'div_2017_all', 'div_2017_cash', 'div_2017_stock',
					'eps_2016', 'yield_2016', 'payout_ratio_2016', 'div_2016_all', 'div_2016_cash', 'div_2016_stock',
					'eps_2015', 'yield_2015', 'payout_ratio_2015', 'div_2015_all', 'div_2015_cash', 'div_2015_stock',
					'eps_2014', 'yield_2014', 'payout_ratio_2014', 'div_2014_all', 'div_2014_cash', 'div_2014_stock',
					'eps_2013', 'yield_2013', 'payout_ratio_2013', 'div_2013_all', 'div_2013_cash', 'div_2013_stock',
					'eps_2012', 'yield_2012', 'payout_ratio_2012', 'div_2012_all', 'div_2012_cash', 'div_2012_stock',
					'eps_2011', 'yield_2011', 'payout_ratio_2011', 'div_2011_all', 'div_2011_cash', 'div_2011_stock',
					'eps_2010', 'yield_2010', 'payout_ratio_2010', 'div_2010_all', 'div_2010_cash', 'div_2010_stock',
					'eps_2009', 'yield_2009', 'payout_ratio_2009', 'div_2009_all', 'div_2009_cash', 'div_2009_stock',
					'eps_2008', 'yield_2008', 'payout_ratio_2008', 'div_2008_all', 'div_2008_cash', 'div_2008_stock',
					'eps_2007', 'yield_2007', 'payout_ratio_2007', 'div_2007_all', 'div_2007_cash', 'div_2007_stock',
					'eps_2006', 'yield_2006', 'payout_ratio_2006', 'div_2006_all', 'div_2006_cash', 'div_2006_stock', 
				]]
								

	df_div.to_csv('history/'+outfile, float_format='%.2f')

	
def readDividenHistory(fname):
	df_eng = pd.read_csv('history/'+fname)
	df_cht = df_eng.rename(columns={'stock': '代碼', 
									'name': '名稱',
									'mean_div_all':'平均股利息',
									'std_div_all':'股息標準差',
									'mean_yield':'平均殖利率',
									'std_yield':'殖利率標準差',
									'mean_payout':'平均配息率',
									'std_payout':'配息率標準差',
									'eps_2018':'2018EPS', 'yield_2018':'2018殖利率', 'payout_ratio_2018':'2018配息率', 'div_2018_all':'2018股利+現金', 'div_2018_cash':'2018現金', 'div_2018_stock':'2018股票',
									'eps_2017':'2017EPS', 'yield_2017':'2017殖利率', 'payout_ratio_2017':'2017配息率', 'div_2017_all':'2017股利+現金', 'div_2017_cash':'2017現金', 'div_2017_stock':'2017股票',
									'eps_2016':'2016EPS', 'yield_2016':'2016殖利率', 'payout_ratio_2016':'2016配息率', 'div_2016_all':'2016股利+現金', 'div_2016_cash':'2016現金', 'div_2016_stock':'2016股票',
									'eps_2015':'2015EPS', 'yield_2015':'2015殖利率', 'payout_ratio_2015':'2015配息率', 'div_2015_all':'2015股利+現金', 'div_2015_cash':'2015現金', 'div_2015_stock':'2015股票',
									'eps_2014':'2014EPS', 'yield_2014':'2014殖利率', 'payout_ratio_2014':'2014配息率', 'div_2014_all':'2014股利+現金', 'div_2014_cash':'2014現金', 'div_2014_stock':'2014股票',
									'eps_2013':'2013EPS', 'yield_2013':'2013殖利率', 'payout_ratio_2013':'2013配息率', 'div_2013_all':'2013股利+現金', 'div_2013_cash':'2013現金', 'div_2013_stock':'2013股票',
									'eps_2012':'2012EPS', 'yield_2012':'2012殖利率', 'payout_ratio_2012':'2012配息率', 'div_2012_all':'2012股利+現金', 'div_2012_cash':'2012現金', 'div_2012_stock':'2012股票',
									'eps_2011':'2011EPS', 'yield_2011':'2011殖利率', 'payout_ratio_2011':'2011配息率', 'div_2011_all':'2011股利+現金', 'div_2011_cash':'2011現金', 'div_2011_stock':'2011股票',
									'eps_2010':'2010EPS', 'yield_2010':'2010殖利率', 'payout_ratio_2010':'2010配息率', 'div_2010_all':'2010股利+現金', 'div_2010_cash':'2010現金', 'div_2010_stock':'2010股票',
									'eps_2009':'2009EPS', 'yield_2009':'2009殖利率', 'payout_ratio_2009':'2009配息率', 'div_2009_all':'2009股利+現金', 'div_2009_cash':'2009現金', 'div_2009_stock':'2009股票',
									'eps_2008':'2008EPS', 'yield_2008':'2008殖利率', 'payout_ratio_2008':'2008配息率', 'div_2008_all':'2008股利+現金', 'div_2008_cash':'2008現金', 'div_2008_stock':'2008股票',
									'eps_2007':'2007EPS', 'yield_2007':'2007殖利率', 'payout_ratio_2007':'2007配息率', 'div_2007_all':'2007股利+現金', 'div_2007_cash':'2007現金', 'div_2007_stock':'2007股票',
									'eps_2006':'2006EPS', 'yield_2006':'2006殖利率', 'payout_ratio_2006':'2006配息率', 'div_2006_all':'2006股利+現金', 'div_2006_cash':'2006現金', 'div_2006_stock':'2006股票',
								})
	return df_eng, df_cht
	
def readBasicInfo():
	df = pd.read_csv('history/basic_info.csv', index_col=0)
	df['股本(億)'] = [x.replace(',', '.') for x in df['股本(億)']]
	df['股本(億)'] = df['股本(億)'].astype(float)	
	df['代號']=df['代號'].str.replace('=', '')
	df['代號']=df['代號'].str.replace('"', '')
	df.rename(columns={'代號': 'stock', '名稱': 'name'}, inplace=True)		
	return df
	
def readGrossMarginProfit12Q():
	df = pd.read_csv('history/gross_profit_margin_12q.csv', index_col=0)
	df['代號']=df['代號'].str.replace('=', '')
	df['代號']=df['代號'].str.replace('"', '')
	df.rename(columns={'代號': 'stock', '名稱': 'name'}, inplace=True)		
	return df	
	
def readNetMarginProfit12Q():
	df = pd.read_csv('history/net_profit_margin_12q.csv', index_col=0)
	df['代號']=df['代號'].str.replace('=', '')
	df['代號']=df['代號'].str.replace('"', '')
	df.rename(columns={'代號': 'stock', '名稱': 'name'}, inplace=True)		
	return df		