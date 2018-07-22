from __future__ import print_function

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
#from pyvirtualdisplay import Display
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from utility import *

#display = Display(visible=0, size=(800, 800))  
#display.start()

driver = webdriver.Chrome('/Users/developer/bin/chromedriver')
#driver.set_window_size(1920, 1080)
driver.get("https://www.tdcc.com.tw/smWeb/QryStock.jsp")


select = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "scaDates")))
#select = driver.find_element_by_id("scaDates")
allOptions = select.find_elements_by_tag_name("option")
optionLen = len(allOptions)
stockList = readStockList('policy/crawl.csv')

for stock in stockList:
	f = None
	#stock = '1101'
	#for i in range(0, optionLen):
	i = 0
	while i < optionLen:
		try:
			select = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "scaDates")))
			#time.sleep(10)
			elem = driver.find_element_by_id("StockNo")
			elem.send_keys(stock)
			elem.send_keys(Keys.RETURN)
			#time.sleep(5)
			allOptions = select.find_elements_by_tag_name("option")
			option = allOptions[i]
			print("Value is: " + option.get_attribute("value"))
			dateStr = option.get_attribute("value")
			option.click()

			elem = driver.find_element_by_name("sub")
			elem.click()
			#time.sleep(5)
			#driver.implicitly_wait(10)
			table = driver.find_elements_by_xpath(("//table[@class='mt']/tbody/tr"));
			
			bGotData = False
			for tr in table:
				_data = tr.text.split(' ')
				if len(_data)==5 and _data[0].isdigit()==True:
					print(tr.text)
					bGotData = True
					if f == None:
						#f = open(u'股權分散表/{}_{}.html'.format(stock, option.get_attribute("value")), mode='w',encoding='utf-8')
						f = open(u'history/share/{}.csv'.format(stock), mode='w',encoding='utf-8')
						print(u'日期,持股,人數,股數,比例', file=f)
					_new_data = []
					for d in _data:
						d = ''.join(i for i in d if i.isdigit() or i in '-.')
						_new_data.append(d)
					_data = _new_data
					new_dateStr = dateStr[0:4]+'-'+dateStr[4:6]+'-'+dateStr[6:8]
					print('{},{},{},{},{}'.format(new_dateStr, _data[1], _data[2], _data[3], _data[4]), file=f)
					#print('{},{},{},{},{}\n'.format(_data[0], _data[1], _data[2], _data[3], _data[4]))
			
			if bGotData == True:
				i = i + 1
			time.sleep(10)

		except:
			driver.refresh()
			time.sleep(10)
			continue


		#break

		#f = open('test{}.html'.format(i), mode='w')
		#f.write(driver.page_source)
		#f.close()
		

	if f != None:
		f.close()
	
#assert "No results found." not in driver.page_source
driver.close()