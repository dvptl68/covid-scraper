import requests
from bs4 import BeautifulSoup

def getData(url): return BeautifulSoup(requests.get(url).content, 'html.parser')

url = 'https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data'
soup = getData(url)
totalData = soup.find(class_='sorttop')
print('Cases: ' + totalData.contents[5].getText(strip=True))
print('Deaths: ' + totalData.contents[7].getText(strip=True))
print('Recoveries: ' + totalData.contents[9].getText(strip=True))