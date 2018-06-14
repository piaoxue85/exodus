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
	df_finacial = pd.read_csv('history/finacial.csv')
	df_finacial = translateFinacialHistory()
	#print(df_finacial)

	df_finacial['std_yield']=pd.Series([float(0)]*len(df_finacial), df_finacial.index)
	df_finacial['std_payout']=pd.Series([float(0)]*len(df_finacial), df_finacial.index)
	df_finacial['mean_yield']=pd.Series([float(0)]*len(df_finacial), df_finacial.index)
	df_finacial['mean_payout']=pd.Series([float(0)]*len(df_finacial), df_finacial.index)

	for index, row in df_finacial.iterrows():
		_yield = [	row['yield_2006'],
					row['yield_2007'],
					row['yield_2008'],
					row['yield_2009'],
					row['yield_2010'],
					row['yield_2011'],
					row['yield_2011'],
					row['yield_2012'],
					row['yield_2013'],
					row['yield_2014'],
					row['yield_2015'],
					row['yield_2016'],
					row['yield_2017']]
		df_finacial.loc[index, 'std_yield'] = np.std(_yield)
		df_finacial.loc[index, 'mean_yield'] = np.mean(_yield)
		_payout = [	row['payout_ratio_2006'],
					row['payout_ratio_2007'],
					row['payout_ratio_2008'],
					row['payout_ratio_2009'],
					row['payout_ratio_2010'],
					row['payout_ratio_2011'],
					row['payout_ratio_2011'],
					row['payout_ratio_2012'],
					row['payout_ratio_2013'],
					row['payout_ratio_2014'],
					row['payout_ratio_2015'],
					row['payout_ratio_2016'],
					row['payout_ratio_2017']]
		df_finacial.loc[index, 'std_payout'] = np.std(_payout)
		df_finacial.loc[index, 'mean_payout'] = np.mean(_payout)

		_div_all = [	row['div_2006_all'],
					row['div_2006_all'],
					row['div_2007_all'],
					row['div_2008_all'],
					row['div_2009_all'],
					row['div_2010_all'],
					row['div_2011_all'],
					row['div_2012_all'],
					row['div_2013_all'],
					row['div_2014_all'],
					row['div_2015_all'],
					row['div_2016_all'],
					row['div_2017_all']]
		df_finacial.loc[index, 'std_div_all'] = np.std(_div_all)
		df_finacial.loc[index, 'mean_div_all'] = np.mean(_div_all)


		#print(_yield)
	print('')
	df_finacial=df_finacial.sort_values(by=['mean_div_all'], ascending=False)
	df_finacial.reset_index(inplace=True)
	df_finacial = df_finacial[	['stock', 'name', 
								'mean_div_all', 'std_div_all',
								'mean_yield', 'std_yield', 'mean_payout', 'std_payout',
								'div_2006_cash', 'div_2007_cash', 'div_2008_cash', 'div_2009_cash',
								'div_2010_cash', 'div_2011_cash', 'div_2012_cash', 'div_2013_cash',
								'div_2014_cash', 'div_2015_cash', 'div_2016_cash', 'div_2017_cash', 'div_2018_cash',
								'div_2006_stock', 'div_2007_stock', 'div_2008_stock', 'div_2009_stock',
								'div_2010_stock', 'div_2011_stock', 'div_2012_stock', 'div_2013_stock',
								'div_2014_stock', 'div_2015_stock', 'div_2016_stock', 'div_2017_stock', 'div_2018_stock',
								'div_2006_all', 'div_2007_all', 'div_2008_all', 'div_2009_all',
								'div_2010_all', 'div_2011_all', 'div_2012_all', 'div_2013_all',
								'div_2014_all', 'div_2015_all', 'div_2016_all', 'div_2017_all', 'div_2018_all',
								'payout_ratio_2006', 'yield_2006', 
								'payout_ratio_2007', 'yield_2007',
								'payout_ratio_2008', 'yield_2008',
								'payout_ratio_2009', 'yield_2009',
								'payout_ratio_2010', 'yield_2010',
								'payout_ratio_2011', 'yield_2011',
								'payout_ratio_2012', 'yield_2012',
								'payout_ratio_2013', 'yield_2013',
								'payout_ratio_2014', 'yield_2014',
								'payout_ratio_2015', 'yield_2015',
								'payout_ratio_2016', 'yield_2016',
								'payout_ratio_2017', 'yield_2017',
								'payout_ratio_2018', 'yield_2018',]]
	df_finacial.to_csv('history/finacial_new.csv', float_format='%.2f')
	writer = pd.ExcelWriter('history/dividen.xlsx')
	df_finacial.to_excel(writer, float_format='%.2f')
	writer.save()
main()