
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
	df = financial_statement(2018, 1, '綜合損益彙總表')
	print(df)
	df = financial_statement(2018, 1, '資產負債彙總表')
	print(df)
	df = financial_statement(2018, 1, '營益分析彙總表')
	print(df)
main()