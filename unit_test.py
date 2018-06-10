
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

def main():
	#update_daily_eps(2018, 1, 31)
	#print(get_daily_eps(2018, 1, 31))
	#empty, df_main = readStockHistory('3014', 9999)
	#stockList = readStockList('all_stock.csv')
	#for stock in stockList:
	#	print(stock)
	#df = financial_statement(2018, 1, '綜合損益彙總表')
	#print(df)
	#df = financial_statement(2018, 1, '資產負債彙總表')
	#print(df)
	#df = financial_statement(2018, 1, '營益分析彙總表')
	#print(df)
	pd.options.display.float_format = '{:.2f}'.format
	df_ROE=readROEHistory('ROE_2006_2017.csv', avg_min=0, std_max=70)
	df_ROE=df_ROE.drop(columns=[u'成交', u'漲跌價', u'漲跌幅', u'18Q1ROE(%)'])
	df_ROE['std_ROE']=df_ROE.std(axis=1, ddof=0)
	#print(df_ROE)
	
	df_ROE=df_ROE.sort_values(by=['avg_ROE'], ascending=False)
	df_ROE=df_ROE[df_ROE['avg_ROE']>0]
	df_ROE=df_ROE[df_ROE['std_ROE']<100]
	df_ROE.reset_index(inplace=True)
	df_ROE=df_ROE[['stock', 'name', 'ranking', 'avg_ROE', 'std_ROE', \
					'2017ROE', '2016ROE', '2015ROE', '2014ROE', '2013ROE', \
					'2012ROE', '2011ROE', '2010ROE', '2009ROE', '2008ROE', \
					'2007ROE', '2006ROE']]
	df_ROE['stock']=df_ROE['stock'].str.replace('=', '')
	df_ROE['stock']=df_ROE['stock'].str.replace('"', '')
	df_ROE.to_csv('test_result/ROE.csv', encoding='utf_8', float_format='%.2f')
	writer = pd.ExcelWriter('test_result/ROE.xlsx')
	df_ROE.to_excel(writer, float_format='%.2f')
	writer.save()
main()