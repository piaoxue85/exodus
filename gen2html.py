from __future__ import print_function
from datetime import date, datetime, timedelta
import json
import pandas as pd

def df2html(df, title, outpath):
	htmlHdr = '<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<title>{}</title>\n\t\t<meta charset=\"UTF-8\">\n\t</head>'.format(title)
	htmlTail = """</html>"""
	_bodyBegin = """
	<body>
	"""
	_bodyEnd = """
	</body>
	"""
	
	_style = """
	<style>
		table, th, td {
		border: 1px solid black;
	}
	</style>	
	"""
	
	tblHdr = """<table style="width:100%">"""
	tblEnd = """</table>"""
	
	_title = "<h1 align=\"center\" style=\"color:blue;\">{}</h1>".format(title)
	
	fhtml = open(outpath, 'w')
	print(htmlHdr, file=fhtml)
	print(_style, file=fhtml)
	print(_bodyBegin, file=fhtml)
	print(_title, file=fhtml)
	print(tblHdr, file=fhtml)
	print('<tr>', file=fhtml)
	for col in df.columns:
		print('<th align=\"left\">{}</th>'.format(col), file=fhtml)
	print('</tr>', file=fhtml)
	
	
	for index, row in df.iterrows():
		print(row.values)
		print('<tr>', file=fhtml)
		_ref = str(row['代碼'])+'_' + row['名稱'] + '/' + 'index.html'
		for val in row.values:
			if type(val) is float:
				print('<td align=\"left\"><a href=\"{}\">{:.2f}</td>'.format(_ref, val), file=fhtml)
			else:
				print('<td align=\"left\"><a href=\"{}\">{}</td>'.format(_ref, val), file=fhtml)
		print('</tr>', file=fhtml)	
	
	print(tblEnd, file=fhtml)	
	print(_bodyEnd, file=fhtml)
	print(htmlTail, file=fhtml)	
	fhtml.close()
	
def genBacis2html(fhtml, df_basic, stock):
	_space = '&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp'
	row = df_basic.loc[df_basic['stock']==stock]
	print('\t<p><b>股本(億)</b>     {}{}<b>市值(億)</b>     {}</p>'.format(row['股本(億)'].values[0], _space, row['市值(億)'].values[0]), file=fhtml)
	print('\t<p><b>成立年數</b>     {}{}<b>上市年數</b>     {}</p>'.format(row['成立年數'].values[0], _space, row['上市年數'].values[0]), file=fhtml)
	print('\t<p><b>產業別</b>     {}{}<b>董事長</b>     {}{}<b>總經理</b>     {}</p>'.format(row['產業別'].values[0], _space, row['董事長'].values[0], _space, row['總經理'].values[0]), file=fhtml)
	
	
def gen2html(stock, name, fname, outpath, imgList, df_basic):

	htmlTail = """</html>"""
	_bodyBegin = """
	<body>
	"""
	_bodyEnd = """
	</body>
	"""
	
	_script = """
    <script type = "text/javascript">
		function picShowPng(name)
        {
            document.getElementById("show_png").src=name;
        }
	</script>
	"""

	htmlHdr = '<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<title>{}</title>\n\t\t<meta charset=\"UTF-8\">\n\t</head>'.format(name)
	try:
		_market = df_basic['市場'][df_basic['stock']==stock].values[0]
	except:
		_market = ''
	_title = "<h1 align=\"center\" style=\"color:blue;\">{}     {}({})</h1>\n".format(stock, name, _market)
	
	fhtml = open(outpath, 'w')
	fhtml.write(htmlHdr)
	print(_script, file=fhtml)
	fhtml.write(_bodyBegin)	
	
	fhtml.write(_title)

	
	try:
		json_data=open(fname)
		info = json.load(json_data)
	except:
		info = {}

	_title = "<h2 style=\"color:red;\">基本資料</h2>"
	print(_title, file=fhtml)
	genBacis2html(fhtml, df_basic, stock)
		
	_title = "<h2 style=\"color:red;\">變因</h2>"
	print(_title, file=fhtml)
	
	# draw factor
	if 'factor' in info:
		for factor in info['factor']['factor']:
			_text = factor['name']
			if factor['effect'] == 'negative':
				effect = '負向'
			else:
				effect = '正向'
			print('\t<p><b>{}</b>     {}</p>'.format(factor['name'], effect), file=fhtml)

	_title = "\t<h2 style=\"color:red;\">新聞</h2>"
	print(_title, file=fhtml)
	if 'news' in info:
		#fhtml.write(_title)
		for news in info['news']['news']:
			print('\t<p><b><font color=\"green\">{}</font></b>     {}</p>'.format(news['date'], news['title']), file=fhtml)
	
	for (img, imgTitle, show) in imgList:
		id = img.split('.')[0]
		_display = 'none'
		_title = '\t<button onclick=\"picShowPng(\'{}\')\">{}</button>'.format(img, imgTitle)
		print(_title, file=fhtml)		

	imageSrc = '<img id=\"show_png\" style=\'height: 100%; width: 100%; object-fit: contain; display: block;\' src=\"{}\"\>'.format(imgList[0][0])
	print(imageSrc, file=fhtml)
	fhtml.write(_bodyEnd)	
	fhtml.write(htmlTail)
	fhtml.close()
	
imgList = 	[
				('price_volume_30.png', '近30日價量', True),
				('revenue.png', '營收', True),
				('EPS.png', 'EPS', True),				
				('price_volume_60.png', '近60日價量', False),
				('price_volume_120.png', '近120日價量', False),
				('price_volume_240.png', '近240日價量', False),
				('price_volume.png', '2013~ 價量', False),
			]
#json2html('factor/9921.json', 'test_result/test1/9921_巨大/9921.html', imgList)
#df = pd.read_csv('test_result/test1/pick.csv', index_col=0)
#df2html(df, 'test1', 'test_result/test1/index.html')
#df2html	