
from __future__ import print_function

import argparse
import numpy as np
import pandas as pd

df = pd.read_csv('history/crude_oil_price.csv')
df['Date'] = pd.to_datetime(df.Date, format='%m-%d-%Y')
df.to_csv('history/crude_oil_price_new.csv', float_format='%.2f')