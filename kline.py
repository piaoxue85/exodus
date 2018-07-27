from __future__ import print_function

import numpy as np
import pandas as pd
from talib.abstract import *
import talib
import matplotlib.pyplot as plt
import matplotlib
import utility

patternFunct = 	{
	'兩烏鴉':talib.CDL2CROWS,
	'三黑鴉':talib.CDL3BLACKCROWS,
	'反攻':talib.CDLCOUNTERATTACK,
	'3內部':talib.CDL3INSIDE,
	'3線打擊':talib.CDL3LINESTRIKE,
	'3外部':talib.CDL3OUTSIDE,
	'南方三星':talib.CDL3STARSINSOUTH,
	'三白兵':talib.CDL3WHITESOLDIERS,
	'頂部棄嬰':talib.CDL3OUTSIDE,
	'大敵當前':talib.CDLADVANCEBLOCK,
	'腰帶線':talib.CDLBELTHOLD,
	'脫離':talib.CDLBREAKAWAY,
	'收盤缺影線':talib.CDLCLOSINGMARUBOZU,
	'藏嬰吞沒':talib.CDLCONCEALBABYSWALL,
	'烏雲壓頂':talib.CDLDARKCLOUDCOVER,
	'十字':talib.CDLDOJI,
	'十字星':talib.CDLDOJISTAR,
	'T十字':talib.CDLDRAGONFLYDOJI,
	'吞噬':talib.CDLENGULFING,
	'十字暮星':talib.CDLEVENINGDOJISTAR,
	'暮星':talib.CDLEVENINGSTAR,
	'跳空並列':talib.CDLGAPSIDESIDEWHITE,
	'倒T十字':talib.CDLGRAVESTONEDOJI,
	'槌子':talib.CDLHAMMER,
	'上吊線':talib.CDLHANGINGMAN,
	'母子線':talib.CDLHARAMI,
	'十字孕線':talib.CDLHARAMICROSS,
	'風高浪大':talib.CDLHIGHWAVE,
	'陷阱':talib.CDLHIKKAKE,
	'修正陷阱':talib.CDLHIKKAKEMOD,
	'家鴿':talib.CDLHOMINGPIGEON,
	'三胞鴉':talib.CDLIDENTICAL3CROWS,
	'頸內線':talib.CDLINNECK,
	'倒頭槌':talib.CDLINVERTEDHAMMER,
	'反沖':talib.CDLKICKING,
	'缺影線反沖':talib.CDLKICKINGBYLENGTH,
	'梯底':talib.CDLLADDERBOTTOM,
	'長腳十字':talib.CDLLONGLEGGEDDOJI,
	'長燭':talib.CDLLONGLINE,
	'缺影線':talib.CDLMARUBOZU,
	'相同低價':talib.CDLMATCHINGLOW,
	'鋪墊':talib.CDLMATHOLD,
	'十字晨星':talib.CDLMORNINGDOJISTAR,
	'晨星':talib.CDLMORNINGSTAR,						
	'頸上線':talib.CDLONNECK,
	'刺透':talib.CDLPIERCING,
	'黃包車夫':talib.CDLRICKSHAWMAN,
	'上升下降三法':talib.CDLRISEFALL3METHODS,
	'分離線':talib.CDLSEPARATINGLINES,
	'射擊之星':talib.CDLSHOOTINGSTAR,
	'短燭':talib.CDLSHORTLINE,
	'紡錘':talib.CDLSPINNINGTOP,
	'停頓':talib.CDLSTALLEDPATTERN,
	'條形三明治':talib.CDLSTICKSANDWICH,
	'探水杆':talib.CDLTAKURI,
	'跳空並列':talib.CDLTASUKIGAP,
	'插入':talib.CDLTHRUSTING,
	'三星':talib.CDLTRISTAR,
	'三河':talib.CDLUNIQUE3RIVER,
	'跳空兩鴉':talib.CDLUPSIDEGAP2CROWS,
	'跳空三法':talib.CDLXSIDEGAP3METHODS,
	'三星':talib.CDLTRISTAR,
}

patternMeaning = 	{
	'兩烏鴉':'下跌',
	'三黑鴉':'下跌',
	'反攻':'持續',
	'3內部':'可能反轉',
	'3線打擊':'上漲',
	'3外部':'可能反轉',
	'南方三星':'上漲',
	'三白兵':'上漲',
	'頂部棄嬰':'反轉',
	'大敵當前':'看淡',
	'腰帶線':'反轉',
	'脫離':'反轉',
	'收盤缺影線':'持續',
	'藏嬰吞沒':'反轉',
	'烏雲壓頂':'下跌',
	'十字':'',
	'十字星':'反轉',
	'T十字':'反轉',
	'吞噬':'反轉',
	'十字暮星':'頂部反轉',
	'暮星':'頂部反轉',
	'跳空並列':'持續',
	'倒T十字':'底部反轉',
	'槌子':'底部反轉',
	'跳空並列':'持續',
	'上吊線':'頂部反轉',
	'母子線':'反轉',
	'十字孕線':'反轉',
	'風高浪大':'反轉',
	'陷阱':'持續',
	'修正陷阱':'持續',
	'家鴿':'反轉',
	'三胞鴉':'下跌',
	'頸內線':'持續',
	'倒頭槌':'反轉',
	'反沖':'反轉',
	'缺影線反沖':'反轉',
	'梯底':'底部反轉',
	'長腳十字':'不確定',
	'長燭':'可能反轉',
	'缺影線':'可能反轉',
	'相同低價':'底部確認',
	'鋪墊':'持續',
	'十字晨星':'底部反轉',
	'晨星':'底部反轉',						
	'頸上線':'持續下跌',
	'刺透':'底部反轉',
	'黃包車夫':'不確定',
	'上升下降三法':'反轉',
	'分離線':'持續',
	'射擊之星':'下跌',
	'短燭':'',
	'紡錘':'可能反轉',
	'停頓':'停頓',
	'條形三明治':'反轉',
	'探水杆':'持續',
	'跳空並列陰陽線':'持續',
	'插入':'持續',
	'三星':'反轉',
	'三河':'反轉',
	'跳空兩鴉':'反轉',
	'跳空三法':'持續',
}

patterncolor = 	{
	'兩烏鴉':'green',
	'三黑鴉':'green',
	'反攻':'blue',
	'3內部':'blue',
	'3線打擊':'green',
	'3外部':'blue',
	'南方三星':'red',
	'三白兵':'red',
	'頂部棄嬰':'blue',
	'大敵當前':'blue',
	'腰帶線':'blue',
	'脫離':'blue',
	'收盤缺影線':'blue',
	'藏嬰吞沒':'red',
	'烏雲壓頂':'green',
	'十字':'blue',
	'十字星':'blue',
	'T十字':'blue',
	'吞噬':'blue',
	'十字暮星':'green',
	'暮星':'green',
	'跳空並列':'blue',
	'倒T十字':'red',
	'槌子':'red',
	'上吊線':'green',
	'母子線':'blue',
	'十字孕線':'blue',
	'風高浪大':'blue',
	'陷阱':'blue',
	'修正陷阱':'blue',
	'家鴿':'blue',
	'三胞鴉':'green',
	'頸內線':'blue',
	'倒頭槌':'blue',
	'反沖':'blue',
	'缺影線反沖':'blue',
	'梯底':'red',
	'長腳十字':'blue',
	'長燭':'blue',
	'缺影線':'blue',
	'相同低價':'blue',
	'鋪墊':'blue',
	'十字晨星':'red',
	'晨星':'red',						
	'頸上線':'green',
	'刺透':'red',
	'黃包車夫':'blue',
	'上升下降三法':'blue',
	'分離線':'blue',
	'射擊之星':'green',
	'短燭':'blue',
	'紡錘':'blue',
	'停頓':'blue',
	'條形三明治':'blue',
	'探水杆':'blue',
	'跳空並列陰陽線':'blue',
	'插入':'blue',
	'三星':'blue',
	'三河':'blue',
	'跳空兩鴉':'blue',
	'跳空三法':'blue',
	}

def kline_meaning(pattern):
	color = 'black'
	if pattern in patterncolor:
		color = patterncolor[pattern]
	meaning = ''
	if pattern in patterncolor:
		meaning = patternMeaning[pattern]
	return (color, meaning)
		
class kline():
	def __init__(self, stock, df):
		self.stock = stock
		self.df = df
		return
		
	def pattern_recogintion(self):
						
		if False:
			vals = talib.CDLCOUNTERATTACK(self.df['open'], self.df['high'], self.df['low'], self.df['close'])
			print('CDLCOUNTERATTACK = ', np.where(vals != 0))
			vals = talib.CDL3WHITESOLDIERS(self.df['open'], self.df['high'], self.df['low'], self.df['close'])
			print('CDL3WHITESOLDIERS = ', np.where(vals != 0))
			vals = talib.CDLADVANCEBLOCK(self.df['open'], self.df['high'], self.df['low'], self.df['close'])
			print('CDLADVANCEBLOCK = ', np.where(vals != 0))
			vals = talib.CDL3BLACKCROWS(self.df['open'], self.df['high'], self.df['low'], self.df['close'])
			print('CDL3BLACKCROWS = ', np.where(vals != 0))
			vals = talib.CDLDARKCLOUDCOVER(self.df['open'], self.df['high'], self.df['low'], self.df['close'])
			print('CDLDARKCLOUDCOVER = ', np.where(vals != 0))
			vals = talib.CDLBREAKAWAY(self.df['open'], self.df['high'], self.df['low'], self.df['close'])
			print('CDLBREAKAWAY = ', np.where(vals != 0))
		
		for pattern, _func in patternFunct.items():
			vals = _func(self.df['open'], self.df['high'], self.df['low'], self.df['close'])
			print(pattern, ' = ', np.where(vals != 0))
			idx = np.where(vals != 0)
			self.df['kline'].iloc[idx] = pattern
		#vals = talib.CDL3WHITESOLDIERS(self.df['open'].values, self.df['high'].values, self.df['low'].values, self.df['close'].values)
		#vals = talib.CDLADVANCEBLOCK(self.df['open'].values, self.df['high'].values, self.df['low'].values, self.df['close'].values)
		#return np.where(vals != 0)
		#return vals
		

