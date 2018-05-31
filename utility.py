from __future__ import print_function

import numpy as np
import pandas as pd
from kd_predict import *
from collections import OrderedDict
import requests
from io import StringIO
from datetime import date, datetime, timedelta
from googlefinance.client import get_price_data, get_prices_data, get_prices_time_data

def tanh_norm(x):
	u = np.mean(x)
	o = np.std(x)
	
	r = 0.01*(x-u)
	r = r/o+1
	r = 0.5*np.tanh(r)
	return r

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

def update_daily_eps(year, month, day):
	datestr = '{}{:02d}{:02d}'.format(year, month, day)
	try:
		r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL')
		df = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
						for i in r.text.split('\n') if len(i.split('",')) == 17 and i[0] != '='])), header=0)
		df.to_csv('history/eps/'+datestr+'.csv')
	except:
		print('unable to get ', datestr)

def daterange(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + timedelta(n)

def update_daily_eps_period(period):
	years = 0
	months = 0
	days = 0
	today = date.today()
	if 'Y' in period:
		years = int(period.rstrip('Y'))
		start_date = today.replace(year=today.year - years)
	if 'M' in period:
		months = int(period.rstrip('M'))
		if (months < today.month):
			start_date = today.replace(month=today.month - months)
		else:
			start_date = today.replace(year=today.year - 1, month=12-(months-today.month))
	if 'd' in period:
		days = int(period.rstrip('d'))
		start_date = datetime.today() - timedelta(days=days)

	for single_date in daterange(start_date, today):
		datestr = '{}{:02d}{:02d}'.format(single_date.year, single_date.month, single_date.day)
		print('update ', datestr)
		update_daily_eps(single_date.year, single_date.month, single_date.day)
		#print(datestr)
	#r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL')
	#df = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '}) 
					#for i in r.text.split('\n') if len(i.split('",')) == 17 and i[0] != '='])), header=0)
	#df.to_csv('history/eps/'+datestr+'.csv')
		
def get_daily_eps(stock, year, month, day):
	datestr = '{}{:02d}{:2d}'.format(year, month, day)
	try:
		df = pd.read_csv('history/'+datestr+'_eps.csv')
		if df.empty == True:
			return 0
		
		df.rename(columns={'本益比': 'eps', '證券代號': 'stock'}, inplace=True)					
		df['stock'] = df['stock'].astype(str)

		eps = df['eps'].loc[df['stock']==stock]
		eps = float(eps.values[0])
		return eps
	except:
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
	r = requests.get(url, headers=headers)
	r.encoding = 'big5'
	html_df = pd.read_html(StringIO(r.text))

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
	df.to_csv('history/{}_{}'.format(year, month)+'_vol.csv')
	
	# 偽停頓
	time.sleep(30)
	return df	