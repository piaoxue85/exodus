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
df_1568['DateStr'] = df_1568['Date'].dt.strftime('%Y-%m-%d')
df_1568.rename(columns={'Open': 'open', 'Close': 'close', \
						'High': 'high', 'Low': 'low', 'Volume': 'volume'
						}, inplace=True)
	
df_1568['k'], df_1568['d'] = talib.STOCH(df_1568['high'], df_1568['low'], df_1568['close'], fastk_period=9)
df_1568 = df_1568.dropna()

#df_1568['longlinecandle'] = talib.CDLLONGLINE(df_1568['open'], df_1568['high'], df_1568['low'], df_1568['close'])
#df_1568['shortlinecandle'] = talib.CDLSHORTLINE(df_1568['open'], df_1568['high'], df_1568['low'], df_1568['close'])
#df_1568['abandonedbaby'] = talib.CDLABANDONEDBABY(df_1568['open'], df_1568['high'], df_1568['low'], df_1568['close'])
#df_1568['breakaway'] = talib.CDLBREAKAWAY(df_1568['open'], df_1568['high'], df_1568['low'], df_1568['close'])
df_1568.reset_index(drop=True, inplace=True)
willr = WILLR(df_1568)

period = 1
df_period = df_1568.loc[range(0, len(df_1568), period)]
df_period.reset_index(drop=True, inplace=True)

if True:

	fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
	ax1_orig_xlim = None
	ax1_txt = None
	ax2_txt = None
	zoom_x_step = [-1, 90, 60, 30, 20, 10, 7, 3]
	current_zoom_x_step_idx = 0

	class SnaptoCursor(object):
		"""
		Like Cursor but the crosshair snaps to the nearest x,y point
		For simplicity, I'm assuming x is sorted
		"""

		def __init__(self, ax1, ax2, df):
			self.ax1 = ax1
			self.ax2 = ax2
			self.df = df
			self.x_df = df['Date']
			self.x_str_df = df['DateStr']
			self.y1_df = df['close']
			self.y2_k_df = df['k']
			self.y2_d_df = df['d']
			self.lx1 = ax1.axhline(color='k', y=self.y1_df.loc[0], linewidth=0.5, linestyle='--')  # the horiz line
			self.ly1 = ax1.axvline(color='k', x=self.x_df.loc[0], linewidth=0.5, linestyle='--')  # the vert line
			self.lx2_k = ax2.axhline(color='k', y=self.y2_k_df.loc[0], linewidth=0.5, linestyle='--')  # the horiz line
			self.ly2_k = ax2.axvline(color='k', x=self.x_df.loc[0], linewidth=0.5, linestyle='--')  # the vert line			
			self.lx2_d = ax2.axhline(color='k', y=self.y2_k_df.loc[0], linewidth=0.5, linestyle='--')  # the horiz line
			self.ly2_d = ax2.axvline(color='k', x=self.x_df.loc[0], linewidth=0.5, linestyle='--')  # the vert line			

			# text location in axes coords
			self.txt1 = self.ax1.text(0, 1.05, "", transform=self.ax1.transAxes)
			self.txt2 = self.ax2.text(0, 1.05, "", transform=self.ax2.transAxes)
			plt.draw()
			return

		def on_scroll(self, event):
			global current_zoom_x_step_idx, zoom_x_step
			
			xdata, ydata = event.xdata, event.ydata
			if event.button == 'up' or event.button == 1:
				current_zoom_x_step_idx = (current_zoom_x_step_idx + 1) % len(zoom_x_step)
			elif (current_zoom_x_step_idx > 0):
				current_zoom_x_step_idx = (current_zoom_x_step_idx - 1) % len(zoom_x_step)
			
			v = np.argmin(np.absolute(date2num(self.x_df)-xdata))
			if (zoom_x_step[current_zoom_x_step_idx] == -1):
				ax1.set_xlim(ax1_orig_xlim)
				ymin = np.min(df_period['k']) if np.min(df_period['k']) < np.min(df_period['d']) else np.min(df_period['d'])
				ymax = np.max(df_period['k']) if np.max(df_period['k']) > np.max(df_period['d']) else np.max(df_period['d'])
				ax2.set_ylim(ymin, ymax)
			else:
				ax1.set_xlim(xdata - zoom_x_step[current_zoom_x_step_idx], xdata + zoom_x_step[current_zoom_x_step_idx])
				ymin = min(	np.min(self.y2_k_df[v-zoom_x_step[current_zoom_x_step_idx]:v+zoom_x_step[current_zoom_x_step_idx]]),
							np.min(self.y2_d_df[v-zoom_x_step[current_zoom_x_step_idx]:v+zoom_x_step[current_zoom_x_step_idx]]))
				ymax = max(	np.max(self.y2_k_df[v-zoom_x_step[current_zoom_x_step_idx]:v+zoom_x_step[current_zoom_x_step_idx]]),
							np.max(self.y2_d_df[v-zoom_x_step[current_zoom_x_step_idx]:v+zoom_x_step[current_zoom_x_step_idx]]))
				ymin = ymin-5 if (ymax-5)>0 else 0
				ymax = ymax+5 if (ymax+5)<100 else 100
				#ymin = np.min(self.y2_k_df[v-zoom_x_step[current_zoom_x_step_idx]:v+zoom_x_step[current_zoom_x_step_idx]])
				#ymax = np.max(self.y2_k_df[v-zoom_x_step[current_zoom_x_step_idx]:v+zoom_x_step[current_zoom_x_step_idx]])

				ax2.set_ylim(ymin, ymax)
				
			plt.draw()
			
			
		def mouse_move(self, event):

			if not event.inaxes:
				return
			
			x, y = event.xdata, event.ydata
			v = np.argmin(np.absolute(date2num(self.x_df)-x))
			x = date2num(self.x_df.loc[v])
			y = self.y1_df.loc[v]
			high = self.df['high'].loc[v]
			low = self.df['low'].loc[v]
			open = self.df['open'].loc[v]
			close = self.df['close'].loc[v]
			self.txt1.set_text('{}  high:{:.2f} low:{:.2f} open:{:.2f} close:{:.2f}'\
								.format(self.x_str_df.loc[v], high, low, open, close))

			self.lx1.set_ydata(y)
			self.ly1.set_xdata(x)
			y = self.y2_k_df.loc[v]
			self.lx2_k.set_ydata(y)
			self.ly2_k.set_xdata(x)
			y = self.y2_d_df.loc[v]
			self.lx2_d.set_ydata(y)
			self.ly2_d.set_xdata(x)
			k = self.y2_k_df.loc[v]
			d = self.y2_d_df.loc[v]
			self.txt2.set_text('K:{:.2f}    D:{:.2f}'.format(k, d))
			
			plt.draw()
			
	ax1.set_title('1568', loc='right')
	# for x-axis tick label
	xtick_locator = AutoDateLocator()
	xtick_formatter = AutoDateFormatter(xtick_locator)
	ax1.xaxis.set_major_locator(xtick_locator)
	ax1.xaxis.set_major_formatter(xtick_formatter)
	# plot the close value
	ax1.plot(df_period['Date'], df_period['close'])
	fig.autofmt_xdate(rotation=30)
	ymin = np.min(df_period['close'])
	ymax = np.max(df_period['close'])
	ax1.set_ylim(ymin, ymax)
	ax1_orig_xlim = ax1.get_xlim()
	ax1.grid()

	# plot the KD
	ax2.plot(df_period['Date'], df_period['k'])
	ax2.plot(df_period['Date'], df_period['d'])
	ax2.legend(['K', 'D'], loc='upper right')	

	
	cursor = SnaptoCursor(ax1, ax2, df_period)
	plt.connect('motion_notify_event', cursor.mouse_move)	
	#plt.connect('scroll_event', cursor.on_scroll)
	plt.connect('button_press_event', cursor.on_scroll)

	ymin = np.min(df_period['close'])
	ymax = np.max(df_period['close'])

	
	#centroid = (df_period['Date'].loc[100], df_period['k'].loc[100])
	#circle1 = plt.Circle(centroid, color='r')
	#ax2.add_artist(circle1)
	ticks = ax2.get_xticks()

	ymin = np.min(df_period['k']) if np.min(df_period['k']) < np.min(df_period['d']) else np.min(df_period['d'])
	ymax = np.max(df_period['k']) if np.max(df_period['k']) > np.max(df_period['d']) else np.max(df_period['d'])
	ymin = ymin-5 if (ymax-5)>0 else 0
	ymax = ymax+5 if (ymax+5)<100 else 100
	ax2.set_ylim(ymin, ymax)
	
	# set mouse scroll event

	ax2.grid()
	plt.show()


	