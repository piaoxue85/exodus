from __future__ import print_function

import numpy as np
import pandas as pd
from talib.abstract import *

import talib

class kd_draw(object):

	def __init__(self, title, ax1, ax2, ax3, df, th):

		self.ax1_orig_xlim = None
		self.ax1_txt = None
		self.ax2_txt = None
		self.zoom_x_step = [-1, 90, 60, 30, 20, 10, 7, 3]
		self.zoom_circle_r = [2, 1, 1, 1, 1, 1, 0.5, 0.2]
		self.current_zoom_x_step_idx = 0

		self.title = title
		self.ax1 = ax1
		self.ax2 = ax2
		self.ax3 = ax3
		self.df = df
		self.th = th
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
		
		self.ly3 = ax3.axvline(color='k', x=self.th['Date'].loc[0], linewidth=0.5, linestyle='--')  # the vert line			
		# text location in axes coords

		self.txt1 = self.ax1.text(0, 1.05, "", transform=self.ax1.transAxes)
		self.txt2 = self.ax2.text(0, 1.05, "", transform=self.ax2.transAxes)
		self.txt3 = self.ax3.text(0, 1.05, "", transform=self.ax3.transAxes)
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
		
		cash = self.th['Cash'].loc[v]
		shares = self.th['Own'].loc[v]
		surplus = self.th['Total'].loc[v]
		self.ly3.set_xdata(x)
		self.txt3.set_text('surplus:{:.2f} cash:{:.2f} shares:{:.2f} '.format(surplus, cash, shares))
		
		plt.draw()

	def draw():
		self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, sharex=True)
		self.ax1.set_title(self.title, loc='right')
		# for x-axis tick label
		xtick_locator = AutoDateLocator()
		xtick_formatter = AutoDateFormatter(xtick_locator)
		self.ax1.xaxis.set_major_locator(xtick_locator)
		self.ax1.xaxis.set_major_formatter(xtick_formatter)

		# plot the close value
		self.ax1.plot(self.df['Date'], self.df['close'])
		self.fig.autofmt_xdate(rotation=30)
		ymin = np.min(self.df['close'])
		ymax = np.max(self.df['close'])
		self.ax1.set_ylim(ymin, ymax)
		self.ax1_orig_xlim = ax1.get_xlim()
		self.ax1.grid()

		# plot the KD
		self.ax2.plot(df_period['Date'], df_period['k'])
		self.ax2.plot(df_period['Date'], df_period['d'])
		self.ax2.legend(['K', 'D'], loc='upper right')	

		
		cursor = SnaptoCursor(ax1, ax2, ax3, df_period, trade_history)
		plt.connect('motion_notify_event', self.mouse_move)	
		#plt.connect('scroll_event', cursor.on_scroll)
		plt.connect('button_press_event', self.on_scroll)
		plt.connect('key_press_event', self.on_key)

		ymin = np.min(df_period['close'])
		ymax = np.max(df_period['close'])
		self.ax1.set_ylim(ymin, ymax)				

class kd_predict():
	def __init__(self, df, initial_cash=100, max=(1, 0.15, 1, 1), \
				overbought_idx=(22, 30, 1, False), oversold_idx=(80, 80, 1, False)):
		self.df = df
		self.initial_cash = initial_cash
		self.cash = initial_cash
		self.shares = 0
		self.avg_price = 0
		self.total = 0
		self.total_invest = 0
		(self.max_win, self.max_loss, self.max_win_step, self.max_loss_step) = max
		(self.ob_k, self.ob_d, self.ob_step, self.ob_cross) = overbought_idx
		(self.os_k, self.os_d, self.os_step, self.os_cross) = oversold_idx
		return
		
	def trade_condition_kd(self, today):
		yesterday = today-1
		rtn = 0
		y_row = self.df.loc[yesterday]
		t_row = self.df.loc[today]
		reason = ''
		# check buy
		if y_row['k'] < self.os_k and y_row['d'] < self.os_d:
			rtn = self.os_step if self.cash >= (self.os_step * t_row['open']) else int(self.cash/t_row['open'])
		
		if rtn > 0 and self.os_cross == True:
			if y_row['k'] >= y_row['d']:
				rtn = 0
		if (rtn != 0):
			reason = 'K {:.1f} D {:.1f}'.format(self.df['k'].loc[yesterday], self.df['d'].loc[yesterday])
			return (rtn, reason)
			
		# check sell
		if y_row['k'] >= self.ob_k and y_row['d'] >= self.ob_d:
			rtn = self.ob_step if self.shares >= self.ob_step else self.shares
		
		if rtn > 0 and self.ob_cross == True:
			if y_row['k'] < y_row['d']:
				rtn = 0
		rtn = rtn * -1
		if (rtn != 0):
			reason = 'K {:.1f} D {:.1f}'.format(self.df['k'].loc[yesterday], self.df['d'].loc[yesterday])
		return (rtn, reason)
		
	def trade_condition_winloss(self, today):
		rtn = 0
		reason = ''
		t_row = self.df.loc[today]
		
		#check sell condition for max win
		if t_row['open'] >= (self.avg_price * (1 + self.max_win)):
			rtn = self.max_win_step if self.shares >= self.max_win_step else self.shares
			reason = 'win {:.2f}'.format(t_row['open']-self.avg_price)
			rtn = rtn * -1
		if (rtn != 0):
			return (rtn, reason) 

		#check sell condition for max loss
		if t_row['open'] <= (self.avg_price * (1 - self.max_loss)):
			rtn = self.max_loss_step if self.shares >= self.max_loss_step else self.shares
			reason = 'loss {:.2f}'.format(self.avg_price-t_row['open'])
			rtn = rtn * -1
		return (rtn, reason)
		
	def transaction_number(self, today):
		(rtn, reason) = self.trade_condition_winloss(today)
		if rtn != 0:
			return (rtn, reason)
		(rtn, reason) = self.trade_condition_kd(today)
		if rtn != 0:
			return (rtn, reason)
		return (0, "")
			
	def investment_return_history(self):
		self.avg_price = 0
		total_invest = 0
		trade_history = []
		print('initial cash {}'.format(self.initial_cash))
		yesterday = None
		self.cash = self.initial_cash
		self.total_invest = 0
		for today in self.df.index:
			buy = 0
			reason = ''
			price = self.df['open'].loc[today]
			date = self.df['Date'].loc[today]
			total_value = self.cash + self.shares * self.df['open'].loc[today]
			if (yesterday == None):
				yesterday = today
				trade_history.append([date, reason, buy, price, self.shares, self.cash, total_value])
				continue

			(buy, reason) = self.transaction_number(today)
			sell = abs(buy)
			if (buy > 0):
				self.shares += buy
				self.total_invest = self.total_invest + buy * price
				self.avg_price = self.total_invest / self.shares
				self.cash = self.cash - buy * price
			elif (sell > 0):
				self.shares -= sell
				self.total_invest = self.total_invest - sell * self.avg_price
				self.cash = self.cash + sell * price

			total_value = self.cash + self.shares * price
			trade_history.append([date, reason, buy, price, self.shares, self.cash, total_value])
			print('trade: {} {} {:.2f} {} {:.2f} {:.2f} '.format(reason.ljust(16), buy, price, self.shares, self.cash, total_value))
			yesterday = today
		return pd.DataFrame(trade_history, columns=['Date', 'Reason', 'Buy', 'Price', 'Own', 'Cash', 'Total'])

	def draw():
		self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, sharex=True)

