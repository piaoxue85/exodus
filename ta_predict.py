from __future__ import print_function

import numpy as np
import pandas as pd
from talib.abstract import *
import talib
import matplotlib.pyplot as plt
import matplotlib
import utility
from matplotlib.ticker import Formatter
from matplotlib.dates import MonthLocator, WeekdayLocator, DayLocator, DateFormatter, AutoDateFormatter, AutoDateLocator, date2num, num2date


class ta_draw(object):

	def __init__(self, title, df, th, pngName=None):
		#matplotlib.rc('font', family='Arial')
		#plt.rc('font', family='simhei')
		plt.rcParams['font.sans-serif'] = ['simhei']
		plt.rcParams['figure.figsize'] = [16, 9]
		self.ax1_orig_xlim = None
		self.ax1_txt = None
		self.ax2_txt = None
		self.zoom_x_step = [-1, 90, 60, 30, 20, 10, 7, 3]
		self.zoom_circle_r = [2, 1, 1, 1, 1, 1, 0.5, 0.2]
		self.current_zoom_x_step_idx = 0

		self.title = title
		self.df = df
		self.th = th
		self.x_df = df['Date']
		self.x_str_df = df['DateStr']
		self.y1_df = df['close']
		self.y2_k_df = df['k']
		self.y2_d_df = df['d']
		self.focus_th_idx = 0
		self.ta_focus_index = 'k'
		self.pngName = pngName

		return
		
	def __del__(self):
		plt.close('all')
		
	def redraw(self, xdata, ydata):
		v = np.argmin(np.absolute(date2num(self.x_df)-xdata))
		if (self.zoom_x_step[self.current_zoom_x_step_idx] == -1):
			self.ax1.set_xlim(self.ax1_orig_xlim)
			ymin = np.min(self.y1_df)
			ymax = np.max(self.y1_df)
			self.ax1.set_ylim(ymin, ymax)				
			ymin = np.min(self.y2_k_df) if np.min(self.y2_k_df) < np.min(self.y2_d_df) else np.min(self.y2_d_df)
			ymax = np.max(self.y2_k_df) if np.max(self.y2_k_df) > np.max(self.y2_d_df) else np.max(self.y2_d_df)
			self.ax2.set_ylim(ymin, ymax)
		else:
			try:
				xmin = date2num(self.x_df[v-self.zoom_x_step[self.current_zoom_x_step_idx]])
				xmax = date2num(self.x_df[v+self.zoom_x_step[self.current_zoom_x_step_idx]])
			except:
				print('error redraw: xdata = {}, v = {}'.format(xdata, v))
				return
			self.ax1.set_xlim(xmin, xmax)
			for c in self.ax2.artists:
				c.width = self.zoom_circle_r[current_zoom_x_step_idx]
				c.height = self.zoom_circle_r[current_zoom_x_step_idx]
			
			ymin = np.min(self.y1_df[v-self.zoom_x_step[self.current_zoom_x_step_idx]:v+self.zoom_x_step[self.current_zoom_x_step_idx]])
			ymax = np.max(self.y1_df[v-self.zoom_x_step[self.current_zoom_x_step_idx]:v+self.zoom_x_step[self.current_zoom_x_step_idx]])
			ymin = ymin * 0.95
			ymax = ymax * 1.05
			self.ax1.set_ylim(ymin, ymax)			
			ymin = min(	np.min(self.y2_k_df[v-self.zoom_x_step[self.current_zoom_x_step_idx]:v+self.zoom_x_step[self.current_zoom_x_step_idx]]),
						np.min(self.y2_d_df[v-self.zoom_x_step[self.current_zoom_x_step_idx]:v+self.zoom_x_step[self.current_zoom_x_step_idx]]))
			ymax = max(	np.max(self.y2_k_df[v-self.zoom_x_step[self.current_zoom_x_step_idx]:v+self.zoom_x_step[self.current_zoom_x_step_idx]]),
						np.max(self.y2_d_df[v-self.zoom_x_step[self.current_zoom_x_step_idx]:v+self.zoom_x_step[self.current_zoom_x_step_idx]]))
			ymin = ymin-5 if (ymax-5)>0 else 0
			ymax = ymax+5 if (ymax+5)<100 else 100
			self.ax2.set_ylim(ymin, ymax)
	
		plt.draw()
		
	def on_scroll(self, event):
		global current_zoom_x_step_idx, zoom_x_step
		
		xdata, ydata = event.xdata, event.ydata
		if event.button == 'up' or event.button == 1:
			if (self.current_zoom_x_step_idx < (len(self.zoom_x_step)-1)):
				self.current_zoom_x_step_idx = (self.current_zoom_x_step_idx + 1) % len(self.zoom_x_step)
		elif (self.current_zoom_x_step_idx > 0):
			self.current_zoom_x_step_idx = (self.current_zoom_x_step_idx - 1) % len(self.zoom_x_step)
		self.redraw(xdata, ydata)
		
	def on_key(self, event):
		global current_zoom_x_step_idx, zoom_x_step

		if (event.xdata == None) or (event.ydata == None):
			return
			
		xdata = event.xdata
		ydata = event.ydata
		v = np.argmin(np.absolute(date2num(self.x_df)-xdata))
		
		# key '0'~'9' is to focus invent policy curve
		if self.th != None and event.key >= '0' and event.key <= '9':
			self.focus_th_idx = int(event.key)
			for _line in self.ax3_lines:
				_line.set_linestyle('--')
				_line.set_linewidth(0.5)
			self.ax3_lines[self.focus_th_idx].set_linestyle('-')
			self.ax3_lines[self.focus_th_idx].set_linewidth(1.5)

			th = self.th[self.focus_th_idx][1]
			cash = th['Cash'].loc[v]
			shares = th['Own'].loc[v]
			surplus = th['Total'].loc[v]
			self.txt3.set_text('surplus:{:.2f} cash:{:.2f} shares:{:.2f} '.format(surplus, cash, shares))
	
			plt.draw()			
			return
			
		if event.key == 'K':
			self.ax2_lines['RSI'].set_linewidth(0.3)
			self.ax2_lines['k'].set_linewidth(1.5)
			self.ax2_lines['d'].set_linewidth(1.5)
			plt.draw()
			return

		if event.key == 'r':
			if self.ta_focus_index == 'k':
				self.ta_focus_index = 'r'
			elif self.ta_focus_index == 'r':
				self.ta_focus_index = 'k'
			self.ax2_lines['RSI'].set_linewidth(0.3)
			self.ax2_lines['k'].set_linewidth(0.3)
			self.ax2_lines['d'].set_linewidth(0.3)
			if (self.ta_focus_index == 'k'):
				self.ax2_lines['k'].set_linewidth(1.5)
				self.ax2_lines['d'].set_linewidth(1.5)
			if (self.ta_focus_index == 'r'):
				self.ax2_lines['RSI'].set_linewidth(1.5)
			plt.draw()
			return
		# key 'up', 'down', 'left', 'right' is to zoom up/down, change focus of datetime

		oldv = v
		if event.key == 'up':
			if (self.current_zoom_x_step_idx < (len(self.zoom_x_step)-1)):
				self.current_zoom_x_step_idx = (self.current_zoom_x_step_idx + 1) % len(self.zoom_x_step)
		if (event.key == 'down') and (self.current_zoom_x_step_idx > 0):
			self.current_zoom_x_step_idx = (self.current_zoom_x_step_idx - 1) % len(self.zoom_x_step)
		if (event.key == 'left'):
			v = v - self.zoom_x_step[self.current_zoom_x_step_idx]
		if (event.key == 'right'):
			v = v + self.zoom_x_step[self.current_zoom_x_step_idx]

		v = v if v > self.zoom_x_step[self.current_zoom_x_step_idx] else self.zoom_x_step[self.current_zoom_x_step_idx]
		v = v if (v + self.zoom_x_step[self.current_zoom_x_step_idx]) < len(self.x_df) else len(self.x_df)-self.zoom_x_step[self.current_zoom_x_step_idx]-1

		print('v {} -> {}, zoom {}'.format(oldv, v, self.zoom_x_step[self.current_zoom_x_step_idx]))

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
		volume = self.df['volume'].loc[v]
		self.txt1.set_text('{}  high:{:.2f} low:{:.2f} open:{:.2f} close:{:.2f}   volume:{}'\
							.format(self.x_str_df.loc[v], high, low, open, close, volume))

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
		RSI = self.df['RSI'].loc[v]
		self.txt2.set_text('K:{:.2f}   D:{:.2f}   RSI:{:.2f}'.format(k, d, RSI))
		
		if self.th != None:
			th = self.th[self.focus_th_idx][1]
			cash = th['Cash'].loc[v]
			shares = th['Own'].loc[v]
			surplus = th['Total'].loc[v]
			self.ly3.set_xdata(x)
			self.txt3.set_text('surplus:{:.2f} cash:{:.2f} shares:{:.2f} '.format(surplus, cash, shares))
		
		plt.draw()

	def draw_basic(self, ax1, ax1_1):
		# set ax1 y lim by close		
		ymin = np.min(self.df['close'])
		ymax = np.max(self.df['close'])
		ax1.set_ylim(ymin*0.85, ymax*1.15)
		# set xlim by date
		ax1.set_xlim(self.df['Date'].loc[0], self.df['Date'].loc[len(self.df['Date'])-1])
		ax1_orig_xlim = ax1.get_xlim()
		# plot the close value
		ax1.plot(self.df['Date'], self.df['close'])
		# draw grid
		ax1.grid()
		
		_text = '收盤價 ' + str(ymin) + ' ~ ' + str(ymax)
		
		
		# set ax1_1 y lim by volume
		ymin = np.min(self.df['volume'].loc[self.df['volume']!=0])
		ymax = np.max(self.df['volume'])
		ax1_1.set_ylim(ymin*0.85, ymax*1.15)
		# set y label for ax1_1
		ax1_1.set_ylabel('Vol')
		# plot the volume value
		ax1_1.plot(self.df['Date'], self.df['volume'], 'C1', label='Vol')
		# draw grid
		ax1_1.grid(color='C1', linestyle='-', linewidth=0.5)
		_text = _text + '    成交量 {:.1f} - {:.1f}'.format(ymin,ymax)
		dateStr = '期間 ' + self.df['DateStr'].loc[:1].values[0] + ' - ' + self.df['DateStr'].tail(1).values[0]
		_text = _text + '  ' + dateStr
		ax1.text(0, 1.02, _text, transform=ax1.transAxes, fontsize=18)		

		# ask matplotlib for the plotted objects and their labels
		lines, labels = ax1.get_legend_handles_labels()
		lines2, labels2 = ax1_1.get_legend_handles_labels()
		ax1_1.legend(lines + lines2, labels + labels2, loc='upper left')			
		
	def draw(self):
		
		if self.th != None:
			self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, sharex=True)
		else:
			self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, sharex=True)
			
		self.ax1_1 = self.ax1.twinx()
		
		# set figure 
		self.fig.suptitle(self.title, fontsize=18)
		self.fig.autofmt_xdate(rotation=70)
		
		self.draw_basic(self.ax1, self.ax1_1)
		
		# plot the KD
		self.ax2_lines = dict()
		self.ax2_lines['k'] = self.ax2.plot(self.df['Date'], self.df['k'])[0]
		self.ax2_lines['d'] = self.ax2.plot(self.df['Date'], self.df['d'])[0]
		# plot RSI		
		self.ax2_lines['RSI'] = self.ax2.plot(self.df['Date'], self.df['RSI'])[0]
		self.ax2_lines['RSI'].set_linewidth(0.3)
		
		self.ax2.legend(['K', 'D', 'RSI'], loc='upper left')	
		
		plt.connect('motion_notify_event', self.mouse_move)	
		#plt.connect('scroll_event', cursor.on_scroll)
		plt.connect('button_press_event', self.on_scroll)
		plt.connect('key_press_event', self.on_key)


		ymin = np.min(self.df['k']) if np.min(self.df['k']) < np.min(self.df['d']) else np.min(self.df['d'])
		ymax = np.max(self.df['k']) if np.max(self.df['k']) > np.max(self.df['d']) else np.max(self.df['d'])
		ymin = ymin-5 if (ymax-5)>0 else 0
		ymax = ymax+5 if (ymax+5)<100 else 100
		self.ax2.set_ylim(ymin, ymax)
		
		# set mouse scroll event

		# draw lines for cursor focus
		self.lx1 = self.ax1.axhline(color='k', y=self.y1_df.loc[0], linewidth=0.5, linestyle='--')  # the horiz line
		self.ly1 = self.ax1.axvline(color='k', x=self.x_df.loc[0], linewidth=0.5, linestyle='--')  # the vert line
		self.lx2_k = self.ax2.axhline(color='k', y=self.y2_k_df.loc[0], linewidth=0.5, linestyle='--')  # the horiz line
		self.ly2_k = self.ax2.axvline(color='k', x=self.x_df.loc[0], linewidth=0.5, linestyle='--')  # the vert line			
		self.lx2_d = self.ax2.axhline(color='k', y=self.y2_k_df.loc[0], linewidth=0.5, linestyle='--')  # the horiz line
		self.ly2_d = self.ax2.axvline(color='k', x=self.x_df.loc[0], linewidth=0.5, linestyle='--')  # the vert line		
		
		# text location in axes coords

		self.txt1 = self.ax1.text(0, 1.05, "", transform=self.ax1.transAxes)
		self.txt2 = self.ax2.text(0, 1.05, "", transform=self.ax2.transAxes)

		if self.th != None:
			self.ax3_lines = []
			for (th_title, th) in self.th:
				marks = th['Date'][th['Buy'] != 0].index.tolist()
				#marks = [1, 3, 5, 7, 9]
				_line = self.ax3.plot(self.df['Date'], th['Total'], label=th_title, marker='.', markevery=marks)
				self.ax3_lines.append(_line[0])
				_line[0].set_linestyle('--')
				_line[0].set_linewidth(0.5)
			self.ax3_lines[self.focus_th_idx].set_linestyle('-')
			self.ax3_lines[self.focus_th_idx].set_linewidth(1.5)		
			lines, labels = self.ax3.get_legend_handles_labels()
			self.ax3.legend(lines, labels, loc='upper left')
			
			#self.ax3.legend(self.focus_th_title, loc='upper right')
			self.ax3.grid()
			th = self.th[self.focus_th_idx][1]
			self.ly3 = self.ax3.axvline(color='k', x=th['Date'].loc[0], linewidth=0.5, linestyle='--')  # the vert line			
			self.txt3 = self.ax3.text(0, 1.05, "", transform=self.ax3.transAxes)			

		
		self.ax2.grid()
		
		# for x-axis tick label
		if len(self.df) < 40:
			self.ax1.xaxis.set_major_locator(DayLocator())
		elif len(self.df) < 100:
			self.ax1.xaxis.set_major_locator(WeekdayLocator())
			self.ax1.xaxis.set_minor_locator(DayLocator())
		else:
			self.ax1.xaxis.set_major_locator(MonthLocator())
			self.ax1.xaxis.set_minor_locator(WeekdayLocator())
		self.ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

		self.ax1.fmt_xdata = DateFormatter('%Y-%m-%d %H:%M:%S')		
		
		
		if self.pngName == None:
			plt.show()		
		else:
			plt.savefig(self.pngName)
			
	def draw_price_volume(self, title=''):
		
		self.fig, self.ax1, = plt.subplots(1, 1, sharex=True)
			
		self.ax1_1 = self.ax1.twinx()
		
		# set figure 
		self.fig.suptitle(self.title+title, fontsize=24)
		self.fig.autofmt_xdate(rotation=70)
		
		self.draw_basic(self.ax1, self.ax1_1)
		if len(self.df) < 40:
			self.ax1.xaxis.set_major_locator(DayLocator())
		elif len(self.df) < 100:
			self.ax1.xaxis.set_major_locator(WeekdayLocator())
			self.ax1.xaxis.set_minor_locator(DayLocator())
		else:
			self.ax1.xaxis.set_major_locator(MonthLocator())
			self.ax1.xaxis.set_minor_locator(WeekdayLocator())
		self.ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
		
		plt.connect('motion_notify_event', self.mouse_move)	
		#plt.connect('scroll_event', cursor.on_scroll)
		plt.connect('button_press_event', self.on_scroll)
		plt.connect('key_press_event', self.on_key)
	
		# set mouse scroll event

		# draw lines for cursor focus
		self.lx1 = self.ax1.axhline(color='k', y=self.y1_df.loc[0], linewidth=0.5, linestyle='--')  # the horiz line
		self.ly1 = self.ax1.axvline(color='k', x=self.x_df.loc[0], linewidth=0.5, linestyle='--')  # the vert line
		
		# text location in axes coords

		self.txt1 = self.ax1.text(0, 1.05, "", transform=self.ax1.transAxes)
		
		if self.pngName == None:
			plt.show()		
		else:
			plt.savefig(self.pngName)			
			
			
	def draw_ta(self, type, pngName):
		self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, sharex=True)
		self.ax1_1 = self.ax1.twinx()
		
		# set figure 
		self.fig.suptitle(self.title + '   ' + type, fontsize=24)
		self.fig.autofmt_xdate(rotation=70)
		
		self.draw_basic(self.ax1, self.ax1_1)
		
		if type == 'KD':
			# plot the KD
			self.ax2_lines = dict()
			self.ax2_lines['k'] = self.ax2.plot(self.df['Date'], self.df['k'])[0]
			self.ax2_lines['d'] = self.ax2.plot(self.df['Date'], self.df['d'])[0]
			# plot RSI		
			self.ax2_lines['RSI'] = self.ax2.plot(self.df['Date'], self.df['RSI'])[0]
			self.ax2_lines['RSI'].set_linewidth(0.3)
			self.ax2.legend(['K', 'D', 'RSI'], loc='upper left')	

		if type == 'SMA':
			# plot the SMA
			self.ax2_lines = dict()
			self.ax2_lines['SMA'] = self.ax2.plot(self.df['Date'], self.df['SMA'])[0]

		if type == 'BIAS':
			# plot the BIAS
			self.ax2_lines = dict()
			self.ax2_lines['BIAS'] = self.ax2.plot(self.df['Date'], self.df['BIAS'])[0]

		if type == 'MACD':
			# plot the MACD
			self.ax2_lines = dict()
			self.ax2_lines['macd'] = self.ax2.plot(self.df['Date'], self.df['macd'])[0]
			self.ax2_lines['macdsignal'] = self.ax2.plot(self.df['Date'], self.df['macdsignal'])[0]
			self.ax2_lines['macdhist'] = self.ax2.plot(self.df['Date'], self.df['macdhist'])[0]
			self.ax2.legend(['MACD', 'Signal', 'HIST'], loc='upper left')	

		if type == 'PER':
			# plot the PER
			self.fig.suptitle(self.title + '   ' + '本益比', fontsize=18)
			self.ax2_lines = dict()
			self.ax2_lines['PER'] = self.ax2.plot(self.df['Date'], self.df['PER'])[0]
			min = self.df['PER'].min()
			max = self.df['PER'].max()
			current = self.df['PER'].tail(1).values[0]
			_text = '本益比 最高 '+ str(max) + ' 最低 ' + str(min) + '   目前 '+str(current)
			self.ax2.text(0, 1.02, _text, transform=self.ax2.transAxes, fontsize=18)

		if type == 'MI_QFIIS':
			# plot the MI_QFIIS
			self.fig.suptitle(self.title + '   ' + '	外資比例', fontsize=18)
			self.ax2_lines = dict()
			self.ax2_lines['MI_QFIIS'] = self.ax2.plot(self.df['Date'], self.df['MI_QFIIS'])[0]
			min = self.df['MI_QFIIS'].loc[self.df['MI_QFIIS']!=0].min()
			max = self.df['MI_QFIIS'].max()
			current = self.df['MI_QFIIS'].tail(1).values[0]
			_text = '外資比例 最高 '+ str(max) + ' 最低 ' + str(min) + '   目前 '+str(current)
			self.ax2.text(0, 1.02, _text, transform=self.ax2.transAxes, fontsize=18)
			
		if type == 'revenue':
			# plot the PER
			self.fig.suptitle(self.title + '   ' + '營收', fontsize=18)
			df_to_draw = self.df[self.df['revenue']!=0]
			self.ax2_lines = dict()
			self.ax2_lines['revenue'] = self.ax2.plot(df_to_draw['Date'], df_to_draw['revenue'])[0]
			try:
				min = self.df['revenue'].loc[self.df['revenue']!=0].min()/1000
				max = self.df['revenue'].max()/1000
				current = self.df['revenue'].loc[self.df['revenue']!=0].tail(1).values[0]/1000
			except:
				min = 0
				max = 0
				current = 0
			_text = '營收(百萬) 最高 {:.1f}  最低 {:.1f}  目前 {:.1f} '.format(max, min, current)
			self.ax2.text(0, 1.02, _text, transform=self.ax2.transAxes, fontsize=18)
			
		# for x-axis tick label
		if len(self.df) < 40:
			self.ax1.xaxis.set_major_locator(DayLocator())
		elif len(self.df) < 100:
			self.ax1.xaxis.set_major_locator(WeekdayLocator())
			self.ax1.xaxis.set_minor_locator(DayLocator())
		else:
			self.ax1.xaxis.set_major_locator(MonthLocator())
			self.ax1.xaxis.set_minor_locator(WeekdayLocator())
		self.ax1.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))

		self.ax1.fmt_xdata = DateFormatter('%Y-%m-%d %H:%M:%S')		
			
			
		if pngName == None:
			plt.show()		
		else:
			plt.savefig(pngName)
			
			
			
class ta_predict():
	def __init__(self, stock, df):
		self.stock = stock
		self.df = df
		return
		
	def transaction_number_by_policy(self, today, buy_tactics, sell_tactics):
		yesterday = today-1
		rtn = 0
		y_row = self.df.loc[yesterday]
		t_row = self.df.loc[today]
		reason = ''
		# check buy
		for tactic in buy_tactics:
			shares_to_buy = tactic['shares']
			buy_reason = tactic['name']
			for cond in tactic['condition']:
				index = cond['index']
				if cond['type'] == 'absolute':
					if 'method' not in list(cond.keys()):
						targetIdx = y_row[index]
						# if can't meet to min/max requirement, don't do
						if targetIdx < cond['min'] or targetIdx > cond['max']:
							shares_to_buy = 0
							break
					else:
						if cond['method'] == 'STD':
							targetIdx = y_row[index]
							_mean = np.mean(self.df[index][:yesterday])
							_std = np.std(self.df[index][:yesterday])
							min = _mean + cond['min']*_std
							max = _mean + cond['max']*_std
							print('check {} : close {}, mean {:.2f}, std {:.2f} ({:.2f}~{:.2f})'.format(t_row['DateStr'], targetIdx, _mean, _std, min, max))
							if targetIdx < min or targetIdx > max:
								shares_to_buy = 0
								break
							
				buy_reason = buy_reason+index+' '+"{:.01f}".format(targetIdx)+','
					
		# check sell
		for tactic in sell_tactics:
			shares_to_sell = tactic['shares'] * -1
			for cond in tactic['condition']:
				index = cond['index']
				if cond['type'] == 'absolute':
					targetIdx = y_row[index]
				if cond['type'] == 'highest_diff_ratio':
					period = cond['period']
					if len(self.df[index][today-period:today]) < period:
						shares_to_sell = 0
						break
					highest = np.max(self.df[index][today-period:today])
					targetIdx = ((t_row[index]-highest)/highest)*100
				# if can't meet to min/max requirement, don't do
				if targetIdx < cond['min'] or targetIdx > cond['max']:
					shares_to_sell = 0
					break
			if shares_to_sell != 0:
				sell_reason = tactic['name']
		
		if shares_to_sell != 0:
			return (shares_to_sell, sell_reason)
		if shares_to_buy != 0:
			return (shares_to_buy, buy_reason)			
		return (0, "")
		
	def investment_return_history_by_policy(self, initial_cash, buy_tactics, sell_tactics):

		self.initial_cash = initial_cash
		self.cash = initial_cash
		self.shares = 0
		self.avg_price = 0
		self.total = 0
		self.total_invest = 0
		trade_history = []
		#print('initial cash {}'.format(self.initial_cash))
		yesterday = None
		for today in self.df.index:
			buy = 0
			reason = ''
			
			price = self.df['open'].loc[today]
			date = self.df['Date'].loc[today]
			df_div = utility.readDividenByStockYear(str(date.year), self.stock)
			try:
				div_stock = df_div['div_stock'].values[0]
				div_cash = df_div['div_cash'].values[0]
				div_stock_date = df_div['div_stock_date'].values[0]
				div_cash_date = df_div['div_cash_date'].values[0]
			except:
				div_stock = 0
				div_cash = 0
				div_stock_date = '0000-00-00'
				div_cash_date = '0000-00-00'
			reason_div = ''
			if (div_stock_date == self.df['DateStr'].loc[today]):
				self.shares = self.shares * (1+div_stock/10)
				self.df['close'][:today] = self.df['close'][:today] / (1+div_stock/10)
				reason_div = 'div stoc '+str(div_stock)
			if (div_cash_date == self.df['DateStr'].loc[today]):
				self.cash = self.cash+self.shares * div_cash
				self.df['close'][:today] = self.df['close'][:today] - div_cash
				reason_div = reason_div + 'div cash '+str(div_cash)
			#print('{} {}:: div {} on {}, {} on {}'.format(self.stock, date.year, div_stock, div_stock_date, div_cash, div_cash_date))
			total_value = self.cash + self.shares * self.df['open'].loc[today]
			if (yesterday == None):
				yesterday = today
				trade_history.append([date, reason, buy, price, self.shares, self.cash, total_value])
				continue

			(buy, reason) = self.transaction_number_by_policy(today, buy_tactics, sell_tactics)

			if True:
				sell = abs(buy)
				if (buy > 0):
					buy = buy if self.cash >= (buy * price) else int(self.cash/price)
					self.shares += buy
					self.total_invest = self.total_invest + buy * price
					self.avg_price = self.total_invest / self.shares
					self.cash = self.cash - buy * price
				elif (sell > 0):
					sell = sell if self.shares >= sell else self.shares
					buy = sell * -1
					self.shares -= sell
					self.total_invest = self.total_invest - sell * self.avg_price
					self.cash = self.cash + sell * price

				total_value = self.cash + self.shares * price
				trade_history.append([date, reason+reason_div, buy, price, self.shares, self.cash, total_value])
			#print('trade {}: {} {} {:.2f} {} {:.2f} {:.2f} '.format(self.df['DateStr'].loc[today], reason.ljust(30), buy, price, self.shares, self.cash, total_value))
			yesterday = today
		return pd.DataFrame(trade_history, columns=['Date', 'Reason', 'Buy', 'Price', 'Own', 'Cash', 'Total'])		


	def is_eligible(self, conditions):

		

		
		(sell_k, sell_d, sell_RSI) = max
		(buy_k, buy_d, buy_RSI) = min
		
		currentK = self.df['k'].tail(1).values[0]
		currentD = self.df['d'].tail(1).values[0]
		currentRSI = self.df['RSI'].tail(1).values[0]
		currentVol = self.df['volume'].tail(1).values[0]
		vol_median = self.df['volume'].tail(10).median()
		if (currentK >= sell_k) and (currentD >= sell_d) and (currentRSI >= sell_RSI):
			return 'SELL'
			
		if (currentK <= buy_k) and (currentD <= buy_d) and (currentRSI <= buy_RSI):
			return 'BUY'
			
		if currentVol >= (1.5 * vol_median) and currentVol > 1000:
			return 'WATCH current {}, median {}'.format(currentVol, vol_median)
			
		return 'Nothing'


