import requests
from bs4 import BeautifulSoup

def getData(url): return BeautifulSoup(requests.get(url).content, 'html.parser')

url = 'https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data'
mainTable = getData(url).find(id='thetable')
data = {}

totalData = mainTable.find(class_='sorttop')
data.update({'worldwide': [totalData.contents[5].getText(strip=True), totalData.contents[7].getText(strip=True), totalData.contents[9].getText(strip=True)]})
print(data)