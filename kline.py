from __future__ import print_function

import numpy as np
import pandas as pd
from talib.abstract import *
import talib
import matplotlib.pyplot as plt
import matplotlib
import utility

class kline():
	def __init__(self, stock, df):
		self.stock = stock
		self.df = df
		return
		
	def pattern_recogintion(self):
		patternFunct = 	{
						'CDLCOUNTERATTACK':talib.CDLCOUNTERATTACK,
						'CDL3WHITESOLDIERS':talib.CDL3WHITESOLDIERS,
						'CDLADVANCEBLOCK':talib.CDLADVANCEBLOCK,
						'CDL3BLACKCROWS':talib.CDL3BLACKCROWS,
						'CDLDARKCLOUDCOVER':talib.CDLDARKCLOUDCOVER,
						'CDLBREAKAWAY':talib.CDLBREAKAWAY,
						'CDLTRISTAR':talib.CDLTRISTAR,
						'十字晨星':talib.CDLMORNINGDOJISTAR,
						'晨星':talib.CDLMORNINGSTAR,
						#'CDLDOJI':talib.CDLDOJI,
						'十字星':talib.CDLDOJISTAR,
						'十字暮星':talib.CDLEVENINGDOJISTAR,
						'暮星':talib.CDLEVENINGSTAR,
						'槌子':talib.CDLHAMMER,
						'CDLCONCEALBABYSWALL':talib.CDLCONCEALBABYSWALL,
						'CDLABANDONEDBABY':talib.CDLABANDONEDBABY,
						}
						
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
		

