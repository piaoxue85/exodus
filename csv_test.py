from __future__ import print_function

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def tanh_norm(x):
	u = np.mean(x)
	o = np.std(x)
	
	r = 0.01*(x-u)
	r = r/o+1
	r = 0.5*np.tanh(r)
	return r
	

df_1568 = pd.read_csv('1568.TW.csv', delim_whitespace=False, header=0)
# remove null data
df_1568 = df_1568.drop(df_1568.index[df_1568.isnull().T.any().T])
df_1568 = df_1568.drop('Adj Close', 1)
df_1568.rename(columns={'Open': 'Open_1568', 'Close': 'Close_1568', \
						'High': 'High_1568', 'Low': 'Low_1568', 'Volume': 'Volume_1568'
						}, inplace=True)


df_0050 = pd.read_csv('0050.TW.csv', delim_whitespace=False, header=0)
# remove null data
df_0050 = df_0050.drop(df_0050.index[df_0050.isnull().T.any().T])
df_0050 = df_0050.drop('Adj Close', 1)
df_0050.rename(columns={'Open': 'Open_0050', 'Close': 'Close_0050', \
						'High': 'High_0050', 'Low': 'Low_0050', 'Volume': 'Volume_0050'
						}, inplace=True)

df_stock = df_0050.merge(df_1568, on=['Date'], how='outer', indicator=True)
df_stock = df_stock.drop(df_stock.index[df_stock._merge.eq('both')==False])
df_stock = df_stock.drop('_merge', 1)

df_ex_rate = pd.read_csv('ExchangeRate.csv', delim_whitespace=False, header=0)
df_ex_rate['Date'] = pd.to_datetime(df_ex_rate.Date)
df_ex_rate['Date'] = df_ex_rate['Date'].dt.strftime('%Y-%02m-%02d')
#print(len(dataframe))

df_all = df_stock.merge(df_ex_rate, on=['Date'], how='outer', indicator=True)
df_all = df_all.drop(df_all.index[df_all._merge.eq('both')==False])

#df_all['Close_0050_Norm'] = df_all['Close_0050']
#df_all['Close_1568_Norm'] = df_all['Close_1568']
#df_all['Buy_Norm'] = df_all['Buy']
df_all['Close_0050_Norm'] = tanh_norm(df_all['Close_0050'])
df_all['Close_1568_Norm'] = tanh_norm(df_all['Close_1568'])
df_all['Buy_Norm'] = tanh_norm(df_all['Buy'])

if True:
	fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
	#fig, ax1 = plt.subplots()

	ax1.plot(df_all['Close_0050_Norm'], 'C0')
	ax1.plot(df_all['Close_1568_Norm'], 'C1')
	ax1.plot(df_all['Buy_Norm'], 'C2')
	ax1.set_title('Stock')
	ax1.legend(['0050', '1568', 'ex.'], loc='upper right')
	#ax1.legend()

	ax2.plot(df_all['Close_0050'], 'C0')
	ax2.plot(df_all['Close_1568'], 'C1')
	ax2.set_title('Stock')
	ax2.legend(['0050', '1568', 'ex.'], loc='upper right')	
	ax3 = ax2.twinx()
	ax3.plot(df_all['Buy'], 'C2')
	ax3.set_ylabel('NTD')
	#loc, labels = ax.xticks()
	ax3.set_xlabel('date')
	
	plt.show()