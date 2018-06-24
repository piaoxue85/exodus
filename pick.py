from __future__ import print_function

import numpy as np
import pandas as pd
from utility import *
import argparse
from collections import OrderedDict
import datetime
import ta_main

def pick_by_policy(df_ROE, df_div, policy):
	reason = ''
	# check buy
	stockList = set(df_ROE['stock'].values.tolist()+df_div['stock'].values.tolist())
	stockList = [s for s in stockList]
	stockList = sorted(stockList)
	pickList = []
	for stock in stockList:
		to_pick = True
		empty, df_price = readStockHistory(stock, 9999, raw=False)
		if empty == True:
			continue
		for cond in policy['tactic']['condition']:
			index = cond['index']
			found_index = False
			if index in df_ROE.columns:
				df = df_ROE
				df = df.loc[df['stock']==stock]
				found_index = True
			if index in df_div.columns:
				df = df_div
				df = df.loc[df['stock']==stock]
				found_index = True
			if (empty == False) and (index in df_price.columns) :
				df = df_price
				found_index = True
			if found_index == False:
				to_pick = False
				break

			period = 1
			if 'period' in cond:
				total = len(df)
				if (total > cond['period']):
					df = df[total-cond['period']:]
			try:
				name = df_ROE['name'][df_ROE['stock']==stock].values[0]
			except:
				name = stock
			price = df_price['close'].tail(1).values[0]
			std_price = np.std(df_price['close'])
			mean_price = np.mean(df_price['close'])
			if cond['type'] == 'absolute':
				targetIdx = np.mean(df[index].values)
				if targetIdx < cond['min'] or targetIdx > cond['max']:
					to_pick = False				
					break
					
			if cond['type'] == 'std_distribution':
				std = np.std(df[index])
				mean = np.mean(df[index])
				df_ok = df[abs(df[index]-mean) <= std*cond['sigma']]
				ratio = float(len(df_ok))/len(df)*100
				if (ratio < cond['ratio']):
					to_pick = False				
					break
					
			if cond['type'] == 'detect_abnormal':
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
						break
					else:
						print('pick {}'.format(stock, len(indexs)))
				if method == 'above_median':
					median = np.mean(df[index])
					
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
	ap.add_argument("-d", "--debug", required=False, default=False, action='store_true')

	args = vars(ap.parse_args())

	pd.options.display.float_format = '{:.2f}'.format
	
	df_ROE=readROEHistory('ROE_2006_2017.csv')
	df_div_eng, _ = readDividenHistory('dividen.csv')
	policy = readPolicy('policy/'+args['pick'])
	pickList = pick_by_policy(df_ROE, df_div_eng, policy)

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
		nameListFile.write('{},{}\n'.format(stock, name))
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
		df_pick = df_pick.append(_new, ignore_index=True)
	
	nameListFile.close()
	df_pick=df_pick.sort_values(by=['平均殖利率'], ascending=False)
	df_pick.reset_index(inplace=True, drop=True)	
	print(df_pick)


	writer = pd.ExcelWriter(path+'/pick.xlsx')
	df_pick.to_excel(writer, float_format='%.2f')
	writer.save()

	if (args['evaluate'] != '') or (args['tindex'] != ''):
		args['file'] = nameListFileName
		args['stock'] = ''
		args['visualize'] = False
		args['path'] = path
		ta_main.main(args)

if __name__ == '__main__':
	main()