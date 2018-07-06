from __future__ import print_function

import argparse
import numpy as np
import pandas as pd
from collections import OrderedDict
from utility import *

def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("-s", "--stock", required=True)
	ap.add_argument("-m", "--market", required=False,  default='TW')
	ap.add_argument("-d", "--debug", required=False, default=False, action='store_true')
	args = vars(ap.parse_args())

	pd.options.display.float_format = '{:.2f}'.format
	ifile = 'history/' + args['stock'] + '.' + args['market'] + '.csv'
	ofile = 'history/' + args['stock'] + '.csv'
	stock = args['stock']
	df_main = pd.read_csv(ifile)
	if df_main.empty == True:
		return
	df_main.rename(columns={'Open': 'open', 'Close': 'close', \
							'High': 'high', 'Low': 'low', 'Volume': 'volume'
							}, inplace=True)
	df_main['Date'] = pd.to_datetime(df_main.Date)
	df_main['DateStr'] = df_main['Date'].dt.strftime('%Y-%m-%d')
	df_main = df_main[['open','high','low','close','volume','Date','DateStr']]	
	if 'eps' not in df_main.columns.values.tolist():
		df_main['eps'] = pd.Series([float(0)]*len(df_main), df_main.index)		
	if 'revenue' not in df_main.columns.values.tolist():
		df_main['revenue'] = pd.Series([float(0)]*len(df_main), df_main.index)
	if 'PER' not in df_main.columns.values.tolist():
		df_main['PER'] = pd.Series([float(0)]*len(df_main), df_main.index)	

	df_main.reset_index(drop=True, inplace=True)
	if args['market'] == 'TWO':
		df_revenue = pd.read_csv('history/revenue/'+stock+'.csv')
	monStr = ['None', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	for index, row in df_main.iterrows():
		dt = row['Date']
		#print('get {} of {}-{}-{}'.format(stock, dt.year, dt.month, dt.day))			
		#eps = get_daily_eps(stock, dt.year, dt.month, dt.day)
		if df_main['PER'].loc[index] == 0:
			per = get_daily_per(stock, dt.year, dt.month, dt.day)
			df_main['PER'].at[index] = per
		if args['market'] == 'TW':
			if df_main['revenue'].loc[index] == 0:
				revenue = get_monthly_revenus(stock, dt.year, dt.month)
				df_main['revenue'].at[index] = revenue
		else:
			mon = monStr[dt.month] + '-' + str(dt.year)[2:]
			try:
				revenue = df_revenue['營業收入'].loc[df_revenue['月別']==mon].values[0]
				revenue = revenue * 100	# in million
			except:
				revenue = 0
			df_main['revenue'].at[index] = revenue
	df_main.to_csv(ofile, float_format='%.2f')
	print('')
main()