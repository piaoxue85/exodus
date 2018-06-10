
from __future__ import print_function

import numpy as np
import pandas as pd
import argparse
from utility import *




def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("-t", "--type", required=False, default='price')
	ap.add_argument("-s", "--start", required=False, default='today')
	ap.add_argument("-p", "--period", required=False, default='1d')
	args = vars(ap.parse_args())	
	
	stocDict = readStockList('all_stock.csv')
	dtype = args['type']
	if args['start'] != 'today':
		startDate = date(int(args['start'].split('-')[0]), int(args['start'].split('-')[1]), int(args['start'].split('-')[2]))
	else:
		startDate = date.today()
	period = args['period']

	if dtype == 'all' or dtype == 'price':
		update_daily(startDate, period)

main()