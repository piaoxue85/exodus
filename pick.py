from __future__ import print_function

import numpy as np
import pandas as pd
from utility import *
import argparse
from collections import OrderedDict
import datetime
import ta_main
import info_main
import gen2html

def select_df_by_index(stock, df_ROE, df_div, df_price, df_basic, index):
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
	if index in df_basic.columns:
		df = df_basic
		found_index = True		
	return found_index, df

def simple_compare(stock, df_ROE, df_div, df_price, df_basic, cond):
	index = cond['index']
	found_index,df = select_df_by_index(stock, df_ROE, df_div, df_price, df_basic, index)
	if found_index == False:
		return False
		

	to_pick = True
	try:
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
	except:
		to_pick = False
	return to_pick
	
def compare_latest_by_ratio(stock, df_ROE, df_div, df_price, df_basic, cond):
	index = cond['index']
	found_index,df = select_df_by_index(stock, df_ROE, df_div, df_price, df_basic, index)
	if found_index == False:
		return False
		

	to_pick = True
	try:
		if cond['method'] == 'mean':
			targetIdx = np.mean(df[index].values)
		if cond['method'] == 'std':
			targetIdx = np.std(df[index].values)
		if cond['method'] == 'median':
			targetIdx = np.median(df[index].values)
		
		ratio = df[index].tail(1).values[0]/targetIdx
			
		if ratio < cond['min'] or ratio > cond['max']:
			to_pick = False				
	except:
		to_pick = False
	return to_pick	

def compare_against_mean_std(stock, df_ROE, df_div, df_price, df_basic, cond):
	index = cond['index']
	found_index,df = select_df_by_index(stock, df_ROE, df_div, df_price, df_basic, index)
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
	
def compare_against_median_std(stock, df_ROE, df_div, df_price, df_basic, cond):
	index = cond['index']
	found_index,df = select_df_by_index(stock, df_ROE, df_div, df_price, df_basic, index)
	if found_index == False:
		return False
	
	period = 1
	if 'period' in cond:
		total = len(df)
		if (total > cond['period']):
			df = df[total-cond['period']:]		
	
	to_pick = True
	std = np.std(df[index])
	mean = np.median(df[index])
	min = mean + std*cond['min']
	max = mean + std*cond['max']
	targetIdx =df_price[index].tail(1).values[0]
	
	if targetIdx < min or targetIdx > max:
		to_pick = False
	print('{} clos {}, std {:.2f}, mean {:.2f}, range {:.2f}-{:.2f}'.format(stock, targetIdx, std, mean, min, max))
	return to_pick	
	
def std_distribution(stock, df_ROE, df_div, df_price, df_basic, cond):
	index = cond['index']
	found_index,df = select_df_by_index(stock, df_ROE, df_div, df_price, df_basic, index)
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
	
def detect_abnormal(stock, df_ROE, df_div, df_price, df_basic, cond):
	index = cond['index']
	found_index,df = select_df_by_index(stock, df_ROE, df_div, df_price, df_basic, index)
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
	'compare_against_median_std': compare_against_median_std,
	'select_df_by_index': select_df_by_index,
	'std_distribution': std_distribution,
	'detect_abnormal': detect_abnormal,
	'compare_latest_by_ratio': compare_latest_by_ratio,
}

def output_div(stock, df_main, df_div_all):
	df = df_div_all.loc[df_div_all['stock'] == stock]
	_field = ['cash', 'stock', 'yield', 'payout_ratio']
	cash_list = []
	stock_list = []
	payout_list = []
	yield_list = []
	eps_list = []
	year_list = []
	for year in range(2006, 2019):
		#df_eps =
		year_list.append(year)
		cash_list.append(df['div_'+str(year)+'_cash'].values[0])
		stock_list.append(df['div_'+str(year)+'_stock'].values[0])
		payout_list.append(df['payout_ratio_'+str(year)].values[0])
		yield_list.append(df['yield_'+str(year)].values[0])
		#eps_list.append(df['div_'+str(year)+'_cash'].values[0]+df['div_'+str(year)+'_stock'].values[0]+1)
		eps_list.append(df['eps_'+str(year)].values[0])
		
	df = pd.DataFrame(	{	
						'year': year_list, 
						'cash': cash_list, 
						'stock': stock_list, 
						'yield':yield_list,
						'payout':payout_list,
						'eps':eps_list,
						})
	df.set_index('year', inplace=True)
	print('')
	return df
	
def pick_by_policy(df_ROE, df_div, df_basic, fname):
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
	reason = []
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
				to_pick = func(stock, df_ROE, df_div, df_price, df_basic[df_basic['stock']==stock], cond)
				if 'comment' in cond:
					if cond['comment'] not in reason:
						reason.append(cond['comment'])
				if to_pick == False:
					break
		else:
			to_pick = True
		if to_pick == True:
			pickList.append((stock, name, price, std_price, mean_price))
			#break
	print('pick ', pickList)
	return pickList, reason

def checkAscendDescend(valList, threshold):
	gradient = []
	score = 0
	for idx in range(len(valList)-1):
		try:
			g = (valList[idx+1] - valList[idx])/valList[idx]
		except:
			continue
		score += (g/threshold)
		if g > threshold:
			gradient.append('ascend')
			#score += (g/threshold)
		elif g < (-1)*threshold:
			gradient.append('descend')
			#score += (g/threshold)
		else:
			gradient.append('not changed')

	_str = ''
	if score > 4:
		_str = '強升'
	elif score > 2:
		_str = '上升'
	elif score > 1:
		_str = '微幅上升'
	elif score < -4:
		_str = '強降'
	elif score < -2:
		_str = '下降'
	elif score < -1:
		_str = '輕微下滑'
	else:
		_str = '無明顯變化'
	return score, _str


def analyzeStock(stock, df_ROE, df_div, df_price, df_basic):
	comment = []
	myROE = df_ROE[df_ROE['stock']==stock]
	avgROE = myROE['avg_ROE'].values[0]
	last5ROE = [myROE['2013ROE'].values[0], myROE['2014ROE'].values[0], myROE['2015ROE'].values[0],
				myROE['2016ROE'].values[0], myROE['2017ROE'].values[0]]
	score, addStr = checkAscendDescend(last5ROE, 0.05)
	addStr = '報酬率' + addStr
	comment.append('過去五年平均股東報酬率 : {:.1f} : {} : '.format(np.mean(last5ROE), addStr))

	avgEPS = np.mean(df_div['eps'])
	last5EPS = df_div['eps'].tail(5).values
	score, addStr = checkAscendDescend(last5EPS, 0.05)
	comment.append('過去五年平均EPS : {:.1f} {} : '.format(np.mean(last5EPS), addStr))

	min = np.min(df_price['close'])
	median = np.median(df_price['close'])
	mean = np.mean(df_price['close'])
	max = np.max(df_price['close'])
	std = np.std(df_price['close'])
	current = df_price['close'].tail(1).values[0]
	comment.append('股價 : {:.1f}~{:.1f}    平均 {:.1f}    中位數 {:.1f}    標準差 {:.1f}    目前 {:.1f}: '.format(
					min, max, mean, median, std, current))	

	df_ok = df_price[abs(df_price['close']-mean) <= std*1]
	ratio = float(len(df_ok))/len(df_price)*100
	comment.append('股價變動 : {:.0f}% 在標準差內 : '.format(ratio))	

	return comment
	
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
	df_basic = readBasicInfo()
	df_div_eng, _ = readDividenHistory('dividen.csv')

	pickList, pick_reason = pick_by_policy(df_ROE, df_div_eng, df_basic, args['pick'])

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
		args['new'] = True
		info_main.drawNew(args)
		
	
	gen2html.df2html(df_pick, args['pick'], path+'/index.html', pick_reason)
	gen2html.genGlobalEconomyhtml(path+'/global.html')

	imgList = 	[
				('price_volume_45.png', '近日價量', True, False),
				('MI_QFIIS_45.png', '近日外資比例', True, False),
				('3j_foreign_45.png', '近日外資進出', True, False),
				('3j_trust_45.png', '近日投信進出', True, False),
				('3j_dealer_45.png', '近日自營商進出', True, False),
				('','',False, False),
				('price_volume_2018.png', '2018價量', True, True),
				('price_volume_2018_5_6.png', '2018(5,6)價量', True, True),
				('price_volume_2018_3_4.png', '2018(3,4)價量', True, True),
				('price_volume_2018_1_2.png', '2018(1,2)價量', True, True),
				('','',False, False),
				('price_volume_2017.png', '2017價量', True, True),
				('price_volume_2017_11_12.png', '2017(11,12)價量', True, True),
				('price_volume_2017_9_10.png', '2017(9,10)價量', True, True),
				('price_volume_2017_7_8.png', '2017(7,8)價量', True, True),
				('price_volume_2017_5_6.png', '2017(5,6)價量', True, True),
				('price_volume_2017_3_4.png', '2017(3,4)價量', True, True),
				('price_volume_2017_1_2.png', '2017(1,2)價量', True, True),
				('','',False, False),
				('price_volume.png', '歷史價量', True, False),
				('MI_QFIIS.png', '歷史外資比例', True, False),
				('3j_foreign.png', '歷史外資進出', True, False),
				('3j_trust.png', '歷史投信進出', True, False),
				('3j_dealer.png', '歷史自營商進出', True, False),
				('','',False, False),				
				('https://www.cmoney.tw/follow/channel/stock-{}?chart=v', '營收', False, False),
				('https://www.cmoney.tw/finance/f00039.aspx?s={}', '主力券商', False, False),
				('https://www.cmoney.tw/follow/channel/stock-{}?chart=e', 'EPS', False, False),
				('https://www.cmoney.tw/follow/channel/stock-{}?chart=f', '利潤率', False, False),
				('margin_12Q.png', '12季毛/淨利率', True, True),
				('share_holders.png', '股權分散表', True, True),
				('https://goodinfo.tw/StockInfo/EquityDistributionClassHis.asp?STOCK_ID={}', 'goodinfo股東分散表', False, False),
				('','',False, False),	
				]

	for (stock, name, _, _, _) in pickList:
		stockPath = path + '/' + stock + '_' + name
		os.makedirs(stockPath, exist_ok=True)
		ipath = stockPath + '/' + 'index.html'
		
		empty, df_price = readStockHistory(stock, 9999, raw=False)
		if empty == True:
			continue		
		df_div = output_div(stock, df_price, df_div_eng)
		comment = analyzeStock(stock, df_ROE, df_div, df_price, df_basic[df_basic['stock']==stock])
		gen2html.gen2html(stock, name, 'factor/'+stock+'.json', ipath, imgList, df_basic, df_price, comment)

if __name__ == '__main__':
	main()