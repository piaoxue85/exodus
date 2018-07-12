from __future__ import print_function
from datetime import date, datetime, timedelta
import json
import pandas as pd

def df2html(df, title, outpath, pick_reason):
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

	_space = '&nbsp&nbsp&nbsp&nbsp&nbsp'
	_title = '綜合'
	_comment = ' 股市/新聞'
	_ref = '<a href=\"{}\">'.format('global.html')
	_reftail = '</a>'	
	print('\t<p>{}<b><font color=\"green\">{}</b>{}{}{}</font></p>'.format(_ref, _title, _reftail, _space, _comment), file=fhtml)	


	_title = "<h2 style=\"color:red;\">挑選條件</h2>"
	print(_title, file=fhtml)
	for reason in pick_reason:
		print('<p><b>{}</b></p>'.format(reason), file=fhtml)

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
	
def genBacis2html(fhtml, df_basic, df_price, stock):
	_title = "<h2 style=\"color:red;\">基本資料</h2>"
	print(_title, file=fhtml)	
	_space = '&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp'
	row = df_basic.loc[df_basic['stock']==stock]
	print('\t<p><b>股本(億)</b>&nbsp&nbsp&nbsp&nbsp{}{}<b>市值(億)</b>&nbsp&nbsp&nbsp&nbsp{}</p>'.format(row['股本(億)'].values[0], _space, row['市值(億)'].values[0]), file=fhtml)
	print('\t<p><b>成立年數</b>&nbsp&nbsp&nbsp&nbsp{}{}<b>上市年數</b>&nbsp&nbsp&nbsp&nbsp{}</p>'.format(row['成立年數'].values[0], _space, row['上市年數'].values[0]), file=fhtml)
	print('\t<p><b>產業別</b>&nbsp&nbsp&nbsp&nbsp{}{}<b>董事長</b>&nbsp&nbsp&nbsp&nbsp{}{}<b>總經理</b>     {}</p>'.format(row['產業別'].values[0], _space, row['董事長'].values[0], _space, row['總經理'].values[0]), file=fhtml)
	print('\t<p><b>外資比例</b>&nbsp&nbsp&nbsp&nbsp{}%&nbsp&nbsp&nbsp({})</p>'.format(df_price['MI_QFIIS'].tail(1).values[0], df_price['DateStr'].tail(1).values[0]), file=fhtml)

def genComment2html(fhtml, comment, stock):
	_title = "<h2 style=\"color:red;\">評價</h2>"
	print(_title, file=fhtml)		
	_space = '&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp'

	for c in comment:
		c = c.replace(' ', '&nbsp')
		print('\t<p><b>{}</b>&nbsp&nbsp&nbsp&nbsp<font color=\"green\">{}&nbsp&nbsp&nbsp&nbsp{}</font></p>'.format(\
					c.split(':')[0], c.split(':')[1], c.split(':')[2]), file=fhtml)
	
def gen2html(stock, name, fname, outpath, imgList, df_basic, df_price, comment):

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
	
	_space = '&nbsp&nbsp&nbsp&nbsp&nbsp'

	htmlHdr = '<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<title>{}</title>\n\t\t<meta charset=\"UTF-8\">\n\t</head>'.format(name)
	try:
		_market = df_basic['市場'][df_basic['stock']==stock].values[0]
	except:
		_market = ''
	_title = "<h1 align=\"center\" style=\"color:blue;\">{}{}{}({})</h1>\n".format(stock, _space, name, _market)
	
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



	genBacis2html(fhtml, df_basic, df_price, stock)
	genComment2html(fhtml, comment, stock)
		
	_title = "<h2 style=\"color:red;\">變因</h2>"
	print(_title, file=fhtml)
	_title = '法人動向'
	_comment = '正向'
	_ref = '<a href=\"https://goodinfo.tw/StockInfo/ShowBuySaleChart.asp?STOCK_ID={}&CHT_CAT=DATE\">'.format(stock)
	_reftail = '</a>'	
	print('\t<p>{}<b><font color=\"green\">{}</b>{}{}{}</font></p>'.format(_ref, _title, _reftail, _space, _comment), file=fhtml)	

	
	# draw factor
	if 'factor' in info:
		for factor in info['factor']['factor']:
			_text = factor['name']
			if factor['effect'] == 'negative':
				effect = '負向'
			else:
				effect = '正向'
			_ref = ''
			_reftail = ''				
			if 'link' in factor:
				_ref = '<a href=\"{}\">'.format(factor['link'])
				_reftail = '</a>'
			comment = factor['comment'] if 'comment' in factor else ''
			print('\t<p>{}<b>{}</b>{}{}{}{}{}</p>'.format(_ref, factor['name'], _reftail, _space, effect, _space, comment), file=fhtml)


	_title = "\t<h2 style=\"color:red;\">資料來源</h2>"
	print(_title, file=fhtml)
	_title = '綜合'
	_comment = '國際 股市/新聞'
	_ref = '<a href=\"{}\">'.format('../global.html')
	_reftail = '</a>'	
	print('\t<p>{}<b><font color=\"green\">{}</b>{}{}{}</font></p>'.format(_ref, _title, _reftail, _space, _comment), file=fhtml)	
	if 'reference' in info:
		#fhtml.write(_title)
		for ref in info['reference']:
			_ref = ''
			_reftail = ''
			if 'link' in ref:
				_ref = '<a href=\"{}\">'.format(ref['link'])
				_reftail = '</a>'
			print('\t<p>{}<b><font color=\"green\">{}</b>{}{}{}</font></p>'.format(_ref, ref['title'], _reftail, _space, ref['comment']), file=fhtml)


	_title = "\t<h2 style=\"color:red;\">新聞</h2>"
	print(_title, file=fhtml)
	if 'news' in info:
		#fhtml.write(_title)
		for news in info['news']['news']:
			_ref = ''
			_reftail = ''
			if 'link' in news:
				_ref = '<a href=\"{}\">'.format(news['link'])
				_reftail = '</a>'
			print('\t<p>{}<b><font color=\"green\">{}</b>{}{}{}</font></p>'.format(_ref, news['date'], _reftail, _space, news['title']), file=fhtml)
			if 'content' in news:
				print('\t<p>{}</p>'.format(news['content']), file=fhtml)
	
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

def genGlobalEconomyhtml(outpath):
	htmlTail = """</html>"""
	_bodyBegin = """
	<body>
	"""
	_bodyEnd = """
	</body>
	"""
	
	_space = '&nbsp&nbsp&nbsp&nbsp&nbsp'
	name = '綜合'
	htmlHdr = '<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<title>{}</title>\n\t\t<meta charset=\"UTF-8\">\n\t</head>'.format(name)

	
	fhtml = open(outpath, 'w')
	fhtml.write(htmlHdr)

	fhtml.write(_bodyBegin)	

	_title = "<h1 align=\"center\" style=\"color:blue;\">{}</h1>\n".format(name)	
	fhtml.write(_title)	
	
	json_data=open('factor/global.json')
	info = json.load(json_data)	
	
	_title = "\t<h2 style=\"color:red;\">資料來源</h2>"
	print(_title, file=fhtml)
	if 'reference' in info:
		#fhtml.write(_title)
		for ref in info['reference']:
			_ref = ''
			_reftail = ''
			if 'link' in ref:
				_ref = '<a href=\"{}\">'.format(ref['link'])
				_reftail = '</a>'
			print('\t<p>{}<b><font color=\"green\">{}</b>{}{}{}</font></p>'.format(_ref, ref['title'], _reftail, _space, ref['comment']), file=fhtml)
	
	_title = "\t<h2 style=\"color:red;\">新聞</h2>"
	print(_title, file=fhtml)
	if 'news' in info:
		for news in info['news']['news']:
			_ref = ''
			_reftail = ''
			if 'link' in news:
				_ref = '<a href=\"{}\">'.format(news['link'])
				_reftail = '</a>'
			print('\t<p>{}<b><font color=\"green\">{}</b>{}{}{}</font></p>'.format(_ref, news['date'], _reftail, _space, news['title']), file=fhtml)
			if 'content' in news:
				print('\t<p>{}</p>'.format(news['content']), file=fhtml)
	
	fhtml.write(_bodyEnd)	
	fhtml.write(htmlTail)
	fhtml.close()

#genGlobalEconomyhtml('test_result/top_watch/'+'global.html')
#json2html('factor/9921.json', 'test_result/test1/9921_巨大/9921.html', imgList)
#df = pd.read_csv('test_result/test1/pick.csv', index_col=0)
#df2html(df, 'test1', 'test_result/test1/index.html')
#df2html	