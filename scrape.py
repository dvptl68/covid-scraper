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

# Dict to store all U.S. counties
allCounties = {}

# Fill counties dict with data from file
with open('locations/us-counties.json') as countyFile:
  allCounties = json.load(countyFile)

# Dict to store all county data
countyData = {}

# Iterate through all states, getting total data
usTable = getData('https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data/United_States_medical_cases_by_state').find('table').find('tbody')
for element in usTable.findAll('tr')[2:-2]:

  # Check if the state is listed before adding data to dict
  stateName = element.findAll('th')[1].getText(strip=True)
  if stateName in states:
    countyData[stateName] = {'Total': list(map(lambda x:x.getText(strip=True), element.findAll('td')[:3]))[:3]}

# Iterate through all states, getting county information
for state in states:

  # Set the name of the sections depending on the state
  extension = 'county'
  if state == 'Alaska':
    extension = 'borough'
  elif state == 'Louisiana':
    extension = 'parish'
  elif state == 'Rhode Island':
    extension = 'municipality'
  
  # Get main data table from Wikipedia COVID-19 page for each state
  searchState = 'Georgia (U.S. state)' if state == 'Georgia' else state
  countyTable = getData(f'https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data/{searchState}_medical_cases_by_{extension}').find('table').find('tbody')

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

    # Remove Wikipedia annotations from name
    try:
      countyName = countyName[:countyName.index('[')]
    except: pass
    
    # Skip rest of loop if retrieved name is not a county
    if countyName not in allCounties[state]: continue

    # Check table for inconsistencies before retrieving county data
    countyNumbers = list(map(lambda x:x.getText(strip=True), element.findAll('td')[:3]))[:3]

    # Add county name and data to dict
    countyData[state].update({countyName: countyNumbers})

with open('locations/test.json', 'w') as out:
  out.write(json.dumps(countyData, indent=2))