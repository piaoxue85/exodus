
from googlefinance.client import get_price_data, get_prices_data, get_prices_time_data
import datetime
import argparse
from utility import *	
from kd_predict import *
import pandas as pd
	
def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("-u", "--update", required=False, default=False, action='store_true')
	args = vars(ap.parse_args())


	now = datetime.datetime.now()
	
	stocDict = readStockList('all_stock.csv')
	
	if args['update'] == True:
		nonExistList = []
		for stock in stocDict:
			
			param = {
				'q': stock, # Stock symbol (ex: "AAPL")
				'i': '86400', # Interval size in seconds ("86400" = 1 day intervals)
				'x': 'TPE', # Stock exchange symbol on which stock is traded (ex: "NASD")
				'p': '1d' # Period (Ex: "1Y" = 1 year)
			}

			df = get_price_data(param)

			if (df.empty):
				print('{} is invalid'.format(stock))
				nonExistList.append(stock)
				continue
			df['Date'] = df.index
			text=df.to_csv(header=False)
			#f = open('history/{}.csv'.format(stock), mode='a')
			#f.write(text)
			#f.close()
			#break

			#print(df)
			#break
	
		for to_del in nonExistList:
			del stocDict[to_del]
		writeStockList('all_stock_new.csv', stocDict)

	for stock in stocDict:
		stockId, stockName = stocDict[stock]
		empty, df_main = readStockHistory(stock)
		if empty == True:
			continue
		predict = ta_predict(df_main)
		decision = predict.is_eligible()
		if decision == 'Nothing':
			continue
		print('{} {}: {}'.format(stock, stockName, decision))
main()		