from __future__ import print_function

import numpy as np
import pandas as pd
from utility import *
import argparse
from collections import OrderedDict
import datetime
import ta_main
import info_main

def select_df_by_index(stock, df_ROE, df_div, df_price, index):
	found_index = False
	to_pick = True
	if index in df_ROE.columns:
		df = df_ROE
		df = df.loc[df['stock']==stock]
		found_index = True
	if index in df_div.columns:
		df = df_div
		df = df.loc[df['stock']==stock]
		found_index = True
	if index in df_price.columns:
		df = df_price
		found_index = True
	return found_index, df

def simple_compare(stock, df_ROE, df_div, df_price, cond):
	index = cond['index']
	found_index,df = select_df_by_index(stock, df_ROE, df_div, df_price, index)
	if found_index == False:
		return False
		

	to_pick = True
	if cond['method'] == 'mean':
		targetIdx = np.mean(df[index].values)
	if cond['method'] == 'std':
		targetIdx = np.std(df[index].values)
	if cond['method'] == 'median':
		targetIdx = np.median(df[index].values)
	if cond['method'] == 'latest':
		targetIdx = df[index].tail(1).values[0]
		
	if targetIdx < cond['min'] or targetIdx > cond['max']:
		to_pick = False				
	
	return to_pick

def compare_against_mean_std(stock, df_ROE, df_div, df_price, cond):
	index = cond['index']
	found_index,df = select_df_by_index(stock, df_ROE, df_div, df_price, index)
	if found_index == False:
		return False
	
	period = 1
	if 'period' in cond:
		total = len(df)
		if (total > cond['period']):
			df = df[total-cond['period']:]		
	
	to_pick = True
	std = np.std(df[index])
	mean = np.mean(df[index])
	min = mean + std*cond['min']
	max = mean + std*cond['max']
	targetIdx =df_price[index].tail(1).values[0]
	
	if targetIdx < min or targetIdx > max:
		to_pick = False
	print('{} clos {}, std {:.2f}, mean {:.2f}, range {:.2f}-{:.2f}'.format(stock, targetIdx, std, mean, min, max))
	return to_pick
	
def std_distribution(stock, df_ROE, df_div, df_price, cond):
	index = cond['index']
	found_index,df = select_df_by_index(stock, df_ROE, df_div, df_price, index)
	if found_index == False:
		return False

	to_pick = True
	period = 1
	if 'period' in cond:
		total = len(df)
		if (total > cond['period']):
			df = df[total-cond['period']:]	
			
	std = np.std(df[index])
	mean = np.mean(df[index])
	df_ok = df[abs(df[index]-mean) <= std*cond['sigma']]
	ratio = float(len(df_ok))/len(df)*100
	if (ratio < cond['ratio']):
		to_pick = False

	return to_pick
	
def detect_abnormal(stock, df_ROE, df_div, df_price, cond):
	index = cond['index']
	found_index,df = select_df_by_index(stock, df_ROE, df_div, df_price, index)
	if found_index == False:
		return False	

	period = 1
	if 'period' in cond:
		total = len(df)
		if (total > cond['period']):
			df = df[total-cond['period']:]		

	to_pick = True
	method = cond['method']
	ratio = cond['ratio']
	times = cond['times']
	interval = cond['interval']
	if method == 'above_mean':
		mean = np.mean(df[index])
		df_ok = df[df[index] >= ratio * mean]
		indexs = df_ok.index
		indexs1 = indexs[1:]
		indexs = indexs[:len(indexs)-1]
		indexs = np.subtract(indexs1,indexs)
		indexs = np.where(indexs <= interval)[0]
		#print('{}: abnormal {}'.format(stock, len(indexs)))
		if len(indexs) < times:
			to_pick = False				
		#else:
		#	print('pick {}'.format(stock, len(indexs)))
		
	return to_pick

funcdict = {
	'simple_compare': simple_compare,
	'compare_against_mean_std': compare_against_mean_std,
	'select_df_by_index': select_df_by_index,
	'std_distribution': std_distribution,
	'detect_abnormal': detect_abnormal,
}

	
def pick_by_policy(df_ROE, df_div, fname):
	reason = ''
	# check buy
	no_condition = False
	
	
	if 'csv' in fname:
		no_condition = True
		stockList = readStockList('policy/'+fname)
	else:
		policy = readPolicy('policy/'+fname)
		stockList = set(df_ROE['stock'].values.tolist()+df_div['stock'].values.tolist())
		stockList = [s for s in stockList]
		stockList = sorted(stockList)
	pickList = []
	for stock in stockList:
		empty, df_price = readStockHistory(stock, 9999, raw=False)
		if empty == True:
			continue
			
		try:
			name = df_ROE['name'][df_ROE['stock']==stock].values[0]
		except:
			name = stock

		price = df_price['close'].tail(1).values[0]
		std_price = np.std(df_price['close'])
		mean_price = np.mean(df_price['close'])
		
		if no_condition == False:
			for cond in policy['tactic']['condition']:

				func = funcdict[cond['function']]
				to_pick = func(stock, df_ROE, df_div, df_price, cond)
				if to_pick == False:
					break
		else:
			to_pick = True
		if to_pick == True:
			pickList.append((stock, name, price, std_price, mean_price))
			#break
	print('pick ', pickList)
	return pickList
	
def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("-p", "--pick", required=False, default='pick0.jason')
	ap.add_argument("-e", "--evaluate", required=False, default='')
	ap.add_argument("-t", "--tindex", required=False, default=False, action='store_true')
	ap.add_argument("-g", "--graphics", required=False, default=False, action='store_true')
	ap.add_argument("-i", "--info", required=False, default=False, action='store_true')
	ap.add_argument("-d", "--debug", required=False, default=False, action='store_true')

	args = vars(ap.parse_args())

	pd.options.display.float_format = '{:.2f}'.format
	
	df_ROE=readROEHistory('ROE_2006_2017.csv')
	df_div_eng, _ = readDividenHistory('dividen.csv')

	pickList = pick_by_policy(df_ROE, df_div_eng, args['pick'])

	if len(pickList) == 0:
		print('No matching!!!')
		return

	# create output folder
	
	path = 'test_result/'+args['pick'].split('.')[0]
	os.makedirs(path, exist_ok=True)

	nameListFileName = path+'/nameList.csv'
	nameListFile = open(nameListFileName, mode='w', encoding="utf-8")

	colList = [	'代碼', '名稱', '股價', '平均股價', '股價標準差',
				'平均配息', '配息標準差',
				'平均殖利率', '殖利率標準差',
				'2018配息', '2018殖利率', 
				'2017配息',	'2017殖利率'
				]
	df_pick = pd.DataFrame(columns=colList) 
	for (stock, name, price, std_price, mean_price) in pickList:

		# write stock list
		try:
			row = df_div_eng.loc[df_div_eng['stock']==stock]
			_mean_div_all = row['mean_div_all'].values[0]
			_std_div_all = row['std_div_all'].values[0]
			_mean_yield = row['mean_yield'].values[0]
			_std_yield = row['std_yield'].values[0]
			_div_2018_all = row['div_2018_all'].values[0]
			_yield_2018 = row['yield_2018'].values[0]
			_div_2017_all = row['div_2017_all'].values[0]
			_yield_2017 = row['yield_2017'].values[0]
			valList = [	stock, name, price, mean_price, std_price,
						_mean_div_all, _std_div_all, 
						_mean_yield, _std_yield,
						_div_2018_all, _yield_2018,
						_div_2017_all, _yield_2017
						]
			_new = pd.DataFrame([valList], columns=colList)
			nameListFile.write('{},{}\n'.format(stock, name))
			df_pick = df_pick.append(_new, ignore_index=True)
		except:
			continue
	
	nameListFile.close()
	df_pick=df_pick.sort_values(by=['平均殖利率'], ascending=False)
	df_pick.reset_index(inplace=True, drop=True)	
	print(df_pick)


	writer = pd.ExcelWriter(path+'/pick.xlsx')
	df_pick.to_excel(writer, float_format='%.2f')
	writer.save()

	if (args['evaluate'] != '') or (args['tindex'] == True):
		args['file'] = nameListFileName
		args['stock'] = ''
		args['visualize'] = False
		args['path'] = path
		ta_main.main(args)
		
	if args['info'] == True:
		args['file'] = nameListFileName
		args['stock'] = ''
		args['visualize'] = False
		args['path'] = path
		info_main.main(args)

if __name__ == '__main__':
	main()