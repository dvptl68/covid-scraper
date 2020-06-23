import requests
from bs4 import BeautifulSoup

# Returns a bs4 object with the parsed HTML from the iven URL
def getData(url): return BeautifulSoup(requests.get(url).content, 'html.parser')

# Get HTML from Wikipedia COVID-19 data page
url = 'https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data'
# Get main data table
mainTable = getData(url).find(id='thetable')
# Dict to store all data
data = {}

# Find worldwide data and add to dict
data.update({'worldwide': list(map(lambda x:x.getText(strip=True), mainTable.find(class_='sorttop').findAll('th')[2:]))[:3]})

# Iterate through all countries in the table
for element in mainTable.find('tbody').findAll('tr'):
  pass

print(data)