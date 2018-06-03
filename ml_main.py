from __future__ import print_function

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter
from talib.abstract import *
from matplotlib.dates import AutoDateFormatter, AutoDateLocator, date2num, num2date
from ml_predict import *
from utility import *
import talib
import argparse
from collections import OrderedDict
import datetime

def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("-f", "--file", required=False, default='focus.csv')
	ap.add_argument("-p", "--period", type=int, required=False, default=9999)
	ap.add_argument("-i", "--initial", required=False, default=1000)
	ap.add_argument("-v", "--visualize", required=False, default=False, action='store_true')
	ap.add_argument("-d", "--debug", required=False, default=False, action='store_true')
	args = vars(ap.parse_args())

	pd.options.display.float_format = '{:.2f}'.format

	stockList = readStockList(args['file'])
	initial_cash = args['initial']
	period = args['period']
	now = datetime.datetime.now()

	for stock in stockList:
		initial_cash = args['initial']
		empty, df_main = readStockHistory(stock, period, raw=False)
		if empty == True:
			continue

		featureNameList = ['open', 'close', 'high', 'low', 'volume', 'eps', 'revenue', 'k', 'd', 'RSI', 'BIAS']
		predict = ml_predict(df_main, featureNameList=featureNameList)
		predict.buildSamples()
		predict.train()
		break
main()