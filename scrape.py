import requests
from bs4 import BeautifulSoup
import json

# Returns a bs4 object with the parsed HTML from the iven URL
def getData(url): return BeautifulSoup(requests.get(url).content, 'html.parser')

# Get main data table from Wikipedia main COVID-19 page
countryTable = getData('https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data').find('table')
# Dict to store all country data
countryData = {}

# Find worldwide data and add to dict
countryData.update({'World': list(map(lambda x:x.getText(strip=True), countryTable.find(class_='sorttop').findAll('th')[2:]))[:3]})

# Iterate through all countries in the table, adding each country name and data to dict
for element in countryTable.find('tbody').findAll('tr')[2:-2]:
  countryData.update({element.find('a').getText(strip=True): list(map(lambda x:x.getText(strip=True), element.findAll('td')[:3]))[:3]})

# List to store all US states
states = []

# Fill states list with data from file
try:
  stateNames = open('locations/us-states.txt', 'r', encoding = 'utf-8')
  states = list(stateNames.read().split('\n'))
finally:
  stateNames.close()

# Dict to store all county data
countyData = {}

# Iterate through all states, getting county information
for state in states:

  # Create key-value pair for the state
  countyData[state] = {}

  # Set the name of the sections depending on the state
  extension = 'county'
  if state == 'Alaska':
    extension = 'borough'
  elif state == 'Louisiana':
    extension = 'parish'
  elif state == 'Rhode Island':
    extension = 'municipality'
  
  # Get main data table from Wikipedia COVID-19 page for each state
  countyTable = getData(f'https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data/{state}_medical_cases_by_{extension}').find('table').find('tbody')

  # Iterate through all sections in table, adding each name and data to dict
  for element in countyTable.findAll('tr')[2:-1 if state == 'Texas' or state == 'West Virginia' or state == 'Wisconsin' else -2]:

    countyName = ''
    countyNumbers = []

    # Check table for inconsistencies before retrieving county name
    if len(element.findAll('th')) == 0:
      countyName = element.find('td').getText(strip=True)
    else:
      if state == 'Wisconsin':
        countyName = element.findAll('th')[1].getText(strip=True)
      else:
        countyName = element.find('th').getText(strip=True)
    
    # Check table for inconsistencies before retrieving county data
    countyNumbers = list(map(lambda x:x.getText(strip=True), element.findAll('td')[:3]))[:3]

    # Remove Wikipedia annotations from name before adding to dict
    try:
      countyData[state].update({countyName[:countyName.index('[')]: countyNumbers})
    except:
      countyData[state].update({countyName: countyNumbers})

with open('locations/test.json', 'w') as countyOut:
  countyOut.write(json.dumps(countyData, indent=2, sort_keys=True))