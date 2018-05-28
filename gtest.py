from googlefinance.client import get_price_data, get_prices_data, get_prices_time_data
param = {
    'q': "2454", # Stock symbol (ex: "AAPL")
    'i': "86400", # Interval size in seconds ("86400" = 1 day intervals)
    #'i': "300", # Interval size in seconds ("86400" = 1 day intervals)
    'x': "TPE", # Stock exchange symbol on which stock is traded (ex: "NASD")
    'p': "5d" # Period (Ex: "1Y" = 1 year)
}

df = get_price_data(param)
print(df)