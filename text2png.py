from __future__ import print_function
import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
from datetime import date, datetime, timedelta
import json

def outputTextToDraw(draw, _text, x_pos, y_pos, fontSize, fontColor):
	font = ImageFont.truetype('simhei.ttf', fontSize)
	wordPerLine = 50
	y_size = 0
	x_size = 0
	for idx in range(0, len(_text), wordPerLine):
		draw.text( (x_pos, y_pos), _text[idx:idx+wordPerLine], fontColor, font=font)
		lineSize = font.getsize(_text[idx:idx+wordPerLine])
		y_pos += lineSize[1]
		y_size += lineSize[1]
		x_size = x_size if lineSize[0] < x_size else lineSize[0]
	return [x_size, y_size]
	
def json2png(fname, outpath, width=1280, height=800):

	json_data=open(fname)
	info = json.load(json_data)

	REPLACEMENT_CHARACTER = u'\uFFFD'
	NEWLINE_REPLACEMENT_STRING = ' ' + REPLACEMENT_CHARACTER + ' '
	leftpadding = 3
	
	today = date.today()
	#prepare linkback
	linkback = 'created on {}-{}-{}'.format(today.year, today.month, today.day)
	fontlinkback = ImageFont.truetype('simhei.ttf', 8)
	linkbackx = fontlinkback.getsize(linkback)[0]
	linkback_height = fontlinkback.getsize(linkback)[1]
	#end of linkback

	img = Image.new("RGBA", (width, height), "#FFF")
	draw = ImageDraw.Draw(img)
	# for title 
	y_pos = 0
	_text = info['id'] + '   ' + info['name']
	y_pos += outputTextToDraw(draw, _text, leftpadding, y_pos, info['fontSize'], info['fontColor'])[1]
	
	# draw factor
	if 'factor' in info:
		size = outputTextToDraw(draw, '變因', leftpadding, y_pos, info['factor']['fontSize'], info['factor']['fontColor'])
		align = leftpadding+size[0]
		y_pos = y_pos + size[1]
		for factor in info['factor']['factor']:
			font = ImageFont.truetype('simhei.ttf', factor['fontSize'])
			_text = factor['name']
			if factor['effect'] == 'negative':
				_text = _text + '   負向'
			else:
				_text = _text + '   正向'
			y_pos += outputTextToDraw(draw, _text, align, y_pos, factor['fontSize'], factor['fontColor'])[1]
	
	# draw news
	if 'news' in info:
		size = outputTextToDraw(draw, '新聞', leftpadding, y_pos, info['news']['fontSize'], info['news']['fontColor'])
		align = leftpadding+size[0]
		y_pos = y_pos + size[1]
		for news in info['news']['news']:
			font = ImageFont.truetype('simhei.ttf', news['fontSize'])
			_text = news['date'] + ': ' + news['title']
			y_pos += outputTextToDraw(draw, _text, align, y_pos, news['fontSize'], news['fontColor'])[1]
			y_pos += 10

	img.save(outpath)	
