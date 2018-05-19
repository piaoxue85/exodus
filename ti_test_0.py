from __future__ import print_function

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import Formatter
from talib.abstract import *
from matplotlib.dates import AutoDateFormatter, AutoDateLocator, date2num, num2date

import talib

def tanh_norm(x):
	u = np.mean(x)
	o = np.std(x)
	
	r = 0.01*(x-u)
	r = r/o+1
	r = 0.5*np.tanh(r)
	return r
	
	
df_1568 = pd.read_csv('1568.TW.csv', delim_whitespace=False, header=0)
# remove null data
df_1568 = df_1568.dropna()
df_1568 = df_1568.drop('Adj Close', 1)
df_1568['Date'] = pd.to_datetime(df_1568.Date)
df_1568.rename(columns={'Open': 'open', 'Close': 'close', \
						'High': 'high', 'Low': 'low', 'Volume': 'volume'
						}, inplace=True)
df_1568.reset_index(drop=True, inplace=True)	
df_1568['k'], df_1568['d'] = talib.STOCH(df_1568['high'], df_1568['low'], df_1568['close'], fastk_period=9)
willr = WILLR(df_1568)

df_0050 = pd.read_csv('0050.TW.csv', delim_whitespace=False, header=0)
# remove null data
df_0050 = df_0050.drop(df_0050.index[df_0050.isnull().T.any().T])
df_0050 = df_0050.drop('Adj Close', 1)
df_0050.rename(columns={'Open': 'open', 'Close': 'close', \
						'High': 'high', 'Low': 'low', 'Volume': 'volume'
						}, inplace=True)

df_ex_rate = pd.read_csv('ExchangeRate.csv', delim_whitespace=False, header=0)
df_ex_rate['Date'] = pd.to_datetime(df_ex_rate.Date)
df_ex_rate['Date'] = df_ex_rate['Date'].dt.strftime('%Y-%02m-%02d')




if True:

	fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
	ax1_orig_xlim = None
	ax1_txt = None
	ax2_txt = None
	zoom_x_step = [-1, 90, 60, 30, 20, 10, 7, 3]
	current_zoom_x_step_idx = 0
	def on_scroll(event):
		global current_zoom_x_step_idx, zoom_x_step
		
		xdata, ydata = event.xdata, event.ydata
		if event.button == 'up':
			current_zoom_x_step_idx = (current_zoom_x_step_idx + 1) % len(zoom_x_step)
		elif (current_zoom_x_step_idx > 0):
			current_zoom_x_step_idx = (current_zoom_x_step_idx - 1) % len(zoom_x_step)
		
		if (zoom_x_step[current_zoom_x_step_idx] == -1):
			ax1.set_xlim(ax1_orig_xlim)
		else:
			ax1.set_xlim(xdata - zoom_x_step[current_zoom_x_step_idx], xdata + zoom_x_step[current_zoom_x_step_idx])
		fig.canvas.draw()
	
	def on_move(event):
		global ax1_txt, ax2_txt
		xdata, ydata = event.xdata, event.ydata
		print('on_move:', event)
		#ax1.text(10, 10, 'here')
		if (event.inaxes != None):
			if event.inaxes == ax1:
				inv = ax1.transData.inverted()
				if (ax1_txt != None):
					ax1_txt.remove()
				val = df_1568[df_1568['Date'] >= num2date(xdata)]# & df_1568['Date'] <= num2date(xdata)]
				val = val[val['Date'] <= num2date(xdata)]
				#(loc_x, loc_y) = inv.transform((xdata, ydata))
				print('on_move:', val)
				#val = str(df_1568['close'].loc(loc_x))
				#ax1_txt = event.inaxes.annotate(val, (xdata, ydata), xycoords='data')
			fig.canvas.draw()
	
	ax1.set_title('1568')
	# for x-axis tick label
	xtick_locator = AutoDateLocator()
	xtick_formatter = AutoDateFormatter(xtick_locator)
	ax1.xaxis.set_major_locator(xtick_locator)
	ax1.xaxis.set_major_formatter(xtick_formatter)
	# plot the close value
	ax1.plot(df_1568['Date'], df_1568['close'])
	fig.autofmt_xdate(rotation=30)

	# plot the KD
	ax2.plot(df_1568['Date'], df_1568['k'])
	ax2.plot(df_1568['Date'], df_1568['d'])
	ax2.legend(['K', 'D'], loc='upper right')	
	ax1_orig_xlim = ax1.get_xlim()
	
	centroid = (df_1568['Date'].loc[100], df_1568['k'].loc[100])
	circle1 = plt.Circle(centroid, color='r')
	ax2.add_artist(circle1)
	
	# set mouse scroll event
	fig.canvas.mpl_connect('scroll_event', on_scroll)
	fig.canvas.mpl_connect('motion_notify_event', on_move)	
	
	plt.show()	
	