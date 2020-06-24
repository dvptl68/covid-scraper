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
data.update({'World': list(map(lambda x:x.getText(strip=True), mainTable.find(class_='sorttop').findAll('th')[2:]))[:3]})

# Iterate through all countries in the table, adding each country name and data to dict
for element in mainTable.find('tbody').findAll('tr')[2:-2]:
  data.update({element.find('a').getText(strip=True): list(map(lambda x:x.getText(strip=True), element.findAll('td')[:3]))[:3]})

# for key in data: print(key + ': ' + '; '.join(data[key]))

# List to store all US states
states = []

# Fill states list with data from file
try:
  stateNames = open('locations/us-states.txt', 'r', encoding = 'utf-8')
  states = list(stateNames.read().split('\n'))
finally:
  stateNames.close()
