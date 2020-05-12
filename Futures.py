from selenium import webdriver
from time import sleep as sl
from selenium.webdriver.support.ui import Select
import re
import pymongo
from selenium.webdriver.chrome.options import Options

client = pymongo.MongoClient("localhost", port = 27017)
db = client.txData12
collection = db.txDec12

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options = chrome_options)
# driver = webdriver.Chrome()

driver.get('https://www.taifex.com.tw/cht/3/futDailyMarketReport')

sl(1)

driver.find_element_by_name('queryDate').clear()
date = driver.find_element_by_name('queryDate')
date.send_keys(r"2019/12/31")
sl(1)

button = driver.find_element_by_name('button')
button.click()
sl(1)

selectop = Select(driver.find_element_by_name('MarketCode'))
selectop.select_by_value("0")
sl(1)

button = driver.find_element_by_name('button')
button.click()
sl(1)

for i in range(31):
    try:
        r_list = driver.find_elements_by_xpath('//*[@id="printhere"]/table/tbody/tr[2]/td/table[2]/tbody/tr')
        date = driver.find_element_by_xpath('//*[@id="printhere"]/table/tbody/tr[2]/td/h3')
        dateString = re.findall(r'\d+[/]\d+[/]\d+', date.text)[0]
        xList = []
        for i in r_list:
            xList.append(i.text.split())
            # print(i.text)

        titleList = xList[0]
        titleList[1] = "".join(titleList[1:4])
        del titleList[2:4]
        titleList[5] = "".join(titleList[5:7])
        del titleList[6]
        titleList.append("日期")

        del xList[-1]
        xList = [i+[dateString] for i in xList]

        for i in xList[1:]:
            dataDict = {}
            for a, b in zip(titleList, i):
                dataDict[a] = b
            # print(dataDict)
            # collection.insert(dataDict)
        print(dateString + " finished.")
        button = driver.find_element_by_name('button3')
        button.click()
        sl(2)
    except Exception as e:
        button = driver.find_element_by_name('button3')
        button.click()
        sl(2)
sl(1)
driver.quit()