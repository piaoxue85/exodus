from __future__ import print_function

import numpy as np
import pandas as pd
from talib.abstract import *
import talib
import matplotlib.pyplot as plt
import matplotlib
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.utils import to_categorical
from keras.layers.recurrent import LSTM

from keras import initializers
from matplotlib.ticker import Formatter
from matplotlib.dates import AutoDateFormatter, AutoDateLocator, date2num, num2date
from sklearn.preprocessing import MinMaxScaler
from utility import *
			
class ml_predict():
	def __init__(self, df, featureNameList):
		self.df = df
		self.df_norm = df.copy()
		self.featureNameList = featureNameList
		scaler = MinMaxScaler(feature_range=(0, 1))

		for col in self.featureNameList:
			#self.df_norm['open'] = min_max_norm(scaler, self.df_norm['open'])
			#self.df_norm['close'] = min_max_norm(scaler, self.df_norm['close'])
			#self.df_norm['high'] = min_max_norm(scaler, self.df_norm['high'])
			#self.df_norm['low'] = min_max_norm(scaler, self.df_norm['low'])
			#self.df_norm['volume'] = min_max_norm(scaler, self.df_norm['volume'])
			#self.df_norm['eps'] = min_max_norm(scaler, self.df_norm['eps'])		
			#self.df_norm['revenue'] = min_max_norm(scaler, self.df_norm['revenue'])
			self.df_norm[col] = min_max_norm(scaler, self.df_norm[col])
		return

	def buildSamples(self, targetName='close', daysPerSample=20):

		dataArray = []
		targetArray = self.df[targetName].values
		for name in self.featureNameList:
			dataArray.append(self.df_norm[name].values)
		dataArray = np.swapaxes(dataArray, 0, 1)
		self.sampleList = []
		self.RiseLabelList = []
		self.FallLabelList = []
		self.priceList = []
		for idx in range(0, len(dataArray)):
			if len(dataArray) < (idx+daysPerSample+1):
				break
			#self.sampleList.append(np.concatenate(dataArray[idx:idx+daysPerSample]))
			self.sampleList.append(dataArray[idx:idx+daysPerSample])
			minPrice = np.min(targetArray[idx:idx+daysPerSample])
			maxPrice = np.max(targetArray[idx:idx+daysPerSample])
			meanPrice = np.mean(targetArray[idx:idx+daysPerSample])
			rise = 1 if targetArray[idx+daysPerSample] > (minPrice*1.01) else 0
			self.RiseLabelList.append(rise)
			fall = 1 if targetArray[idx+daysPerSample] < (maxPrice*0.93) else 0
			self.FallLabelList.append(rise)

			self.priceList.append(targetArray[idx+daysPerSample])
		print(self.sampleList)

	def train(self, train_split=0.9):
		
		kernel_init=initializers.RandomUniform(minval=-0.05, maxval=0.05, seed=None)
		
		# establish model
		model = Sequential()
		model.add(LSTM(256, input_shape=(len(self.sampleList[0]), len(self.sampleList[0][0])), return_sequences=True))
		model.add(Dropout(0.5))
		model.add(LSTM(256, input_shape=(len(self.sampleList[0]), len(self.sampleList[0][0])), return_sequences=False))
		model.add(Dense(256, 
						kernel_initializer=kernel_init,
						activation='sigmoid'))
		model.add(Dropout(0.5))
		model.add(Dense(128, 
						kernel_initializer=kernel_init,
						activation='relu'))
		model.add(Dropout(0.5))
		model.add(Dense(2, activation='softmax'))
		#model.add(Dense(1, activation='linear'))

		model.compile(optimizer='adam',
	              		loss='binary_crossentropy',
	              		metrics=['accuracy'])

		#model.compile(optimizer='adam',
	    #           		loss='mse',
	    #          		metrics=['accuracy'])	    

		model.summary()

		input_data = np.asarray(self.sampleList)
		input_label = to_categorical(np.asarray(self.RiseLabelList))
		#input_label = np.asarray(self.priceList)
		#history = model.fit(input_data, input_label, validation_split=0.2, epochs=500, batch_size=10)
		history = model.fit(input_data, input_label, validation_split=0.1, epochs=100, batch_size=50)
		#for layer in model.layers:
		#	weights = layer.get_weights()
		first = model.layers[0].get_weights() #input to hidden
		first = np.array(first[0])
		print(first)
		
	def transaction_number(self, today):
		return (0, "")
			
	def investment_return_history(self, initial_cash=100):

		self.initial_cash = initial_cash
		self.cash = initial_cash
		self.shares = 0
		self.avg_price = 0
		self.total = 0
		self.total_invest = 0


	def is_eligible(self):
			
		return 'Nothing'
