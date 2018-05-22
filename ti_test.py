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

def kd_find_overbought_cross(df):
	ob = (df['k'] >= 80) & (df['d'] >= 70) & (df['k'] < df['d'])
	return ob

def kd_find_oversold_cross(df):
	ob = (df['k'] < 22) & (df['d'] < 30) & (df['k'] > df['d'])
	return ob

def investment_return_history_by_kd(df, max_loss=0.15, max_win=0.30):
	max_invest = 0
	money = 100
	shares = 0
	invest = []
	trade_history = []
	print('initial money {}'.format(money))
	for idx in df.index:
		buy = 0
		if (df['oversold_cross'].loc[idx] == True) and (money >= df['open'].loc[idx+1]):

			#print('{} K={:.1f}, D={:.1f} buy {:.2f} , money = {:.2f}, shares {}'.format(\
			#				df['DateStr'].loc[idx+1], \
			#				df['k'].loc[idx], df['d'].loc[idx], \
			#				df['open'].loc[idx+1], money, shares))
			reason = 'K {:.1f} D {:.1f}'.format(df['k'].loc[idx], df['d'].loc[idx])
			buy = 1
			price = df['open'].loc[idx+1]
			date = df['DateStr'].loc[idx+1]
			invest.append((df['DateStr'].loc[idx+1], buy, df['open'].loc[idx+1]))

		if df['overbought_cross'].loc[idx] == True and shares > 0:
			#print('{} K={:.1f}, D={:.1f} sold {:.2f} , money = {:.2f}, shares {}'.format(\
			#					df['DateStr'].loc[idx+1], \
			#					df['k'].loc[idx], df['d'].loc[idx], \
			#					df['open'].loc[idx+1], money, shares))
			reason = 'K {:.1f} D {:.1f}'.format(df['k'].loc[idx], df['d'].loc[idx])
			buy = -1
			price = df['open'].loc[idx+1]
			date = df['DateStr'].loc[idx+1]

		if (buy != 0):
			shares = shares + buy
			money = money - (buy * price)
			total_value = money + shares * price
			trade_history.append([date, reason, buy, price, shares, money, total_value])

		for (d, s, p) in invest:
			buy = 0
			if df['open'].loc[idx] >= (p * (1+max_win)):
				buy = -1 * s
				price = df['open'].loc[idx]
				date = date = df['DateStr'].loc[idx]
				#print('{} org={:.2f} sold {:.2f}x{} , money = {:.2f}, shares {}'.format(\
				#				df['DateStr'].loc[idx], \
				#				p, \
				#				df['open'].loc[idx], s, \
				#				money, shares))
				reason = 'win {:.2f}'.format(price-p)
			if df['open'].loc[idx] < (p * (1-max_loss)):
				buy = -1 * s
				price = df['open'].loc[idx]
				reason = 'loss {:.2f}'.format(p-price)
				#print('{} org={:.2f} sold {:.2f}x{} , money = {:.2f}, shares {}'.format(\
				#				df['DateStr'].loc[idx], \
				#				p, \
				#				df['open'].loc[idx], s, \
				#				money, shares))

			if buy != 0:
				price = df['open'].loc[idx]
				date = date = df['DateStr'].loc[idx]
				money = money - (buy * price)
				shares = shares + buy
				total_value = money + shares * price
				trade_history.append([date, reason, buy, price, shares, money, total_value])
				invest.remove((d, s, p))


		#print('buy {:.2f} , total in stock {:.2f}'.format(df['open'].loc[idx+1], money))
		
	return pd.DataFrame(trade_history, columns=['Date', 'Reason', 'Buy', 'Price', 'Own', 'Cash', 'Total'])

pd.options.display.float_format = '{:.2f}'.format

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
df_1568['overbought_cross'] = pd.Series(kd_find_overbought_cross(df_1568))
df_1568['oversold_cross'] = pd.Series(kd_find_oversold_cross(df_1568))
df_1568.reset_index(drop=True, inplace=True)

trade_history = investment_return_history_by_kd(df_1568)
#print('return = shares {}, money {:.2f}'.format(shares, money))

#df_1568['longlinecandle'] = talib.CDLLONGLINE(df_1568['open'], df_1568['high'], df_1568['low'], df_1568['close'])
#df_1568['shortlinecandle'] = talib.CDLSHORTLINE(df_1568['open'], df_1568['high'], df_1568['low'], df_1568['close'])
#df_1568['abandonedbaby'] = talib.CDLABANDONEDBABY(df_1568['open'], df_1568['high'], df_1568['low'], df_1568['close'])
#df_1568['breakaway'] = talib.CDLBREAKAWAY(df_1568['open'], df_1568['high'], df_1568['low'], df_1568['close'])

willr = WILLR(df_1568)

period = 1
df_period = df_1568.loc[range(0, len(df_1568), period)]
df_period.reset_index(drop=True, inplace=True)



if False:

	fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
	ax1_orig_xlim = None
	ax1_txt = None
	ax2_txt = None
	zoom_x_step = [-1, 90, 60, 30, 20, 10, 7, 3]
	zoom_circle_r = [2, 1, 1, 1, 1, 1, 0.5, 0.2]
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
			
			
		def redraw(self, xdata, ydata):
			global current_zoom_x_step_idx, zoom_x_step
			v = np.argmin(np.absolute(date2num(self.x_df)-xdata))
			if (zoom_x_step[current_zoom_x_step_idx] == -1):
				ax1.set_xlim(ax1_orig_xlim)
				ymin = np.min(self.y1_df)
				ymax = np.max(self.y1_df)
				ax1.set_ylim(ymin, ymax)				
				ymin = np.min(self.y2_k_df) if np.min(self.y2_k_df) < np.min(self.y2_d_df) else np.min(self.y2_d_df)
				ymax = np.max(self.y2_k_df) if np.max(self.y2_k_df) > np.max(self.y2_d_df) else np.max(self.y2_d_df)
				ax2.set_ylim(ymin, ymax)
			else:
				try:
					xmin = date2num(self.x_df[v-zoom_x_step[current_zoom_x_step_idx]])
					xmax = date2num(self.x_df[v+zoom_x_step[current_zoom_x_step_idx]])
				except:
					print('error redraw: xdata = {}, v = {}'.format(xdata, v))
					return
				ax1.set_xlim(xmin, xmax)
				for c in ax2.artists:
					c.width = zoom_circle_r[current_zoom_x_step_idx]
					c.height = zoom_circle_r[current_zoom_x_step_idx]
				
				ymin = np.min(self.y1_df[v-zoom_x_step[current_zoom_x_step_idx]:v+zoom_x_step[current_zoom_x_step_idx]])
				ymax = np.max(self.y1_df[v-zoom_x_step[current_zoom_x_step_idx]:v+zoom_x_step[current_zoom_x_step_idx]])
				ymin = ymin * 0.95
				ymax = ymax * 1.05
				ax1.set_ylim(ymin, ymax)			
				ymin = min(	np.min(self.y2_k_df[v-zoom_x_step[current_zoom_x_step_idx]:v+zoom_x_step[current_zoom_x_step_idx]]),
							np.min(self.y2_d_df[v-zoom_x_step[current_zoom_x_step_idx]:v+zoom_x_step[current_zoom_x_step_idx]]))
				ymax = max(	np.max(self.y2_k_df[v-zoom_x_step[current_zoom_x_step_idx]:v+zoom_x_step[current_zoom_x_step_idx]]),
							np.max(self.y2_d_df[v-zoom_x_step[current_zoom_x_step_idx]:v+zoom_x_step[current_zoom_x_step_idx]]))
				ymin = ymin-5 if (ymax-5)>0 else 0
				ymax = ymax+5 if (ymax+5)<100 else 100
				ax2.set_ylim(ymin, ymax)
				
			plt.draw()

		def on_scroll(self, event):
			global current_zoom_x_step_idx, zoom_x_step
			
			xdata, ydata = event.xdata, event.ydata
			if event.button == 'up' or event.button == 1:
				if (current_zoom_x_step_idx < (len(zoom_x_step)-1)):
					current_zoom_x_step_idx = (current_zoom_x_step_idx + 1) % len(zoom_x_step)
			elif (current_zoom_x_step_idx > 0):
				current_zoom_x_step_idx = (current_zoom_x_step_idx - 1) % len(zoom_x_step)
			self.redraw(xdata, ydata)
			
		def on_key(self, event):
			global current_zoom_x_step_idx, zoom_x_step

			if (event.xdata == None) or (event.ydata == None):
				return
			xdata = event.xdata
			ydata = event.ydata
			v = np.argmin(np.absolute(date2num(self.x_df)-xdata))
			oldv = v
			if event.key == 'up':
				if (current_zoom_x_step_idx < (len(zoom_x_step)-1)):
					current_zoom_x_step_idx = (current_zoom_x_step_idx + 1) % len(zoom_x_step)
			if (event.key == 'down') and (current_zoom_x_step_idx > 0):
				current_zoom_x_step_idx = (current_zoom_x_step_idx - 1) % len(zoom_x_step)
			if (event.key == 'left'):
				v = v - zoom_x_step[current_zoom_x_step_idx]
			if (event.key == 'right'):
				v = v + zoom_x_step[current_zoom_x_step_idx]

			v = v if v > zoom_x_step[current_zoom_x_step_idx] else zoom_x_step[current_zoom_x_step_idx]
			v = v if (v + zoom_x_step[current_zoom_x_step_idx]) < len(self.x_df) else len(self.x_df)-zoom_x_step[current_zoom_x_step_idx]-1

			print('v {} -> {}, zoom {}'.format(oldv, v, zoom_x_step[current_zoom_x_step_idx]))

			xdata = date2num(self.x_df[v])

			self.redraw(xdata, ydata)
			
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
	plt.connect('key_press_event', cursor.on_key)

	ymin = np.min(df_period['close'])
	ymax = np.max(df_period['close'])
	ax1.set_ylim(ymin, ymax)
	
	for idx in df_1568[df_1568['oversold_cross']==True].index:
		centroid = (date2num(df_period['Date'].loc[idx]), df_period['k'].loc[idx])
		c = plt.Rectangle(centroid, 2, 2, color='r')
		c.label = str(idx)
		ax2.add_artist(c)
		centroid = (date2num(df_period['Date'].loc[idx]), df_period['d'].loc[idx])
		c.label = str(idx)
		c = plt.Rectangle(centroid, 2, 2, color='r')
		ax2.add_artist(c)

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


	