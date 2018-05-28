
from __future__ import print_function

import numpy as np
#import pandas as pd
#from googlefinance.client import get_price_data, get_prices_data, get_prices_time_data


def readStockList(fname):
	_stock = dict()
	f = open(fname, mode='r', encoding="utf-8")
	for line in f:
		#print(line)
		line = line.replace('\n', '').replace('\t', ' ').rstrip()
		item = line.split()
		if '' in item:
			print(line)
		for i in range(0, len(item), 2):
			id = item[i]
			name = item[i+1]
			_stock[id] = (id, name)
	f.close()
	return _stock	



def main():
	stocDict = readStockList('stock.csv')
	print('stocDict = ', stocDict)
	f = open('all_stock.csv', mode='w', encoding="utf-8")
	for stock in stocDict:
		(id, name) = stocDict[stock]
		f.write(id+','+name+'\n')
	f.close()
main()