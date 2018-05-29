
from __future__ import print_function

import numpy as np
import pandas as pd
import requests
from io import StringIO
from utility import *
import time


def monthly_report(year, month):
    
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

def main():
	monthly_report(2018, 1)
	monthly_report(2018, 2)
	monthly_report(2018, 3)
	monthly_report(2018, 4)
	#for year in range(2014, 2018):
	#	for month in range(1, 13):
	#		monthly_report(year, month)
main()