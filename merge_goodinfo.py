
from __future__ import print_function

import datetime
import argparse
import pandas as pd
import os

def main():

	ap = argparse.ArgumentParser()
	ap.add_argument("-p", "--path", required=False, default='/Users/developer/Downloads/')
	ap.add_argument("-o", "--output", required=True)
	ap.add_argument("-r", "--rename", required=False, default='')
	args = vars(ap.parse_args())

	_new = True
	for f in os.listdir(args['path']):
		if f.startswith('Stock') and f.endswith('.csv'):
			if _new == True:
				df = pd.read_csv(args['path']+f)
				_new = False
				continue
			df_new = pd.read_csv(args['path']+f)
			df = df.append(df_new)
			if args['rename'] != '':
				os.rename(args['path']+f, args['path']+args['rename']+f)

	sort_field = df.columns.values[0]
	df = df.sort_values(sort_field)
	df.reset_index(drop=True, inplace=True)
	df.to_csv(args['output'])

main()

