import requests
from bs4 import BeautifulSoup
import json

# Returns a bs4 object with the parsed HTML from the iven URL
def getData(url): return BeautifulSoup(requests.get(url).content, 'html.parser')

# Get main data table from Wikipedia COVID-19 page
countryTable = getData('https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data').find('table')
# Dict to store all country data
countryData = {}

# Find worldwide data and add to dict
countryData.update({'World': list(map(lambda x:x.getText(strip=True), countryTable.find(class_='sorttop').findAll('th')[2:]))[:3]})

# Iterate through all countries in the table, adding each country name and data to dict
for element in countryTable.find('tbody').findAll('tr')[2:-2]:
  countryData.update({element.find('a').getText(strip=True): list(map(lambda x:x.getText(strip=True), element.findAll('td')[:3]))[:3]})

# for key in countryData: print(key + ': ' + '; '.join(data[key]))

# List to store all US states
states = []

# Fill states list with data from file
try:
  stateNames = open('locations/us-states.txt', 'r', encoding = 'utf-8')
  states = list(stateNames.read().split('\n'))
finally:
  stateNames.close()

# Dict to store all county data
counties = {}

# Iterate through all states, getting county information
for state in states:
  counties[state] = []
  extension = 'county'
  if state == 'Alaska':
    extension = 'borough'
  elif state == 'Louisiana':
    extension = 'parish'
  elif state == 'Rhode Island':
    extension = 'municipality'
  countyTable = getData(f'https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data/{state}_medical_cases_by_{extension}').find('table').find('tbody')
  for element in countyTable.findAll('tr')[2:-1 if state == 'Texas' or state == 'West Virginia' or state == 'Wisconsin' else -2]:      
    text = ''
    if len(element.findAll('th')) == 0:
      text = element.find('td').getText(strip=True)
    else:
      if state == 'Wisconsin':
        text = element.findAll('th')[1].getText(strip=True)
      else:
        text = element.find('th').getText(strip=True)
    try:
      counties[state].append(text[:text.index('[')])
    except:
      counties[state].append(text)

with open('locations/test.json', 'w') as countyOut:
  countyOut.write(json.dumps(counties, indent=2, sort_keys=True))