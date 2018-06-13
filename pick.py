from __future__ import print_function

import numpy as np
import pandas as pd
from utility import *
import argparse
from collections import OrderedDict
import datetime

def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--initial", required=False, default=1000)
	ap.add_argument("-e", "--evaluate", required=False, default='')
	ap.add_argument("-v", "--visualize", required=False, default=False, action='store_true')
	ap.add_argument("-d", "--debug", required=False, default=False, action='store_true')
	args = vars(ap.parse_args())

	pd.options.display.float_format = '{:.2f}'.format
	
	df_ROE=readROEHistory('ROE_2006_2017.csv')
	#df_finacial = pd.read_csv('history/finacial.csv')
	df_finacial = translateFinacialHistory()
	print(df_finacial)
	
	df_finacial.to_csv('history/finacial.csv')
main()