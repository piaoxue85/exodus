from googlefinance.client import get_price_data, get_prices_data, get_prices_time_data
import datetime

def readStockList(fname):
	_stock = dict()
	f = open(fname, mode='r', encoding="utf-8")
	for line in f:
		w = line.replace('\n', '').split(',')
		_stock[w[0]] = (w[0], w[1])
	f.close()
	return _stock	

now = datetime.datetime.now()
stocDict = readStockList('all_stock.csv')
print('stocDict = ', stocDict)
for stock in stocDict:
	param = {
	    'q': stock, # Stock symbol (ex: "AAPL")
	    'i': "86400", # Interval size in seconds ("86400" = 1 day intervals)
	    #'i': "300", # Interval size in seconds ("86400" = 1 day intervals)
	    'x': "TPE", # Stock exchange symbol on which stock is traded (ex: "NASD")
	    'p': "1" # Period (Ex: "1Y" = 1 year)
	}
	df = get_price_data(param)
	if (df.empty):
		continue
	df['Date'] = df.index
	text=df.to_csv(header=False)
	f = open('history/{}.csv'.format(stock), mode='a')
	f.write(text)
	f.close()
	print('Get {} : {}'.format(stock, text))
	#print(df)
	#break