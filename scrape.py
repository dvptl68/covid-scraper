import requests
from bs4 import BeautifulSoup
import json
import smtplib
import email.message

# Returns a bs4 object with the parsed HTML from the given URL
def getData(url): return BeautifulSoup(requests.get(url).content, 'html.parser')

# Function to scrape Wikipedia page for country data
def getCountryData(countryData):

  # Get main data table from Wikipedia main COVID-19 page
  countryTable = getData('https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data').find('table')

  # Find total worldwide data and add to dict
  countryData.update({'Total': list(map(lambda x: x.getText(strip=True), countryTable.find(class_='sorttop').findAll('th')[2:]))[:3]})

  # Iterate through all countries in the table, adding each country name and data to dict
  for element in countryTable.find('tbody').findAll('tr')[2:-2]:
    countryData.update({element.find('a').getText(strip=True): list(map(lambda x: x.getText(strip=True), element.findAll('td')[:3]))[:3]})
  
  return countryData

# Function to scrape Wikipedia page for state data
def getStateData(countyData, states):

  # Get main data table from Wikipedia US states COVID-19 page
  usTable = getData('https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data/United_States_medical_cases_by_state').find('table').find('tbody')

  # Iterate through all states, getting total data
  for element in usTable.findAll('tr')[2:-2]:

    # Check if the state is listed before adding data to dict
    stateName = element.findAll('th')[1].getText(strip=True)

    if stateName in states.keys():
      countyData[stateName] = {'Total': list(map(lambda x: x.getText(strip=True), element.findAll('td')[:3]))[:3]}

# Function to scrape Wikipedia page for county data
def getCountyData(countyData, states, allCounties):

  # Iterate through all states, getting county information
  for state in states.keys():

    # Set the name of the sections depending on the state
    extension = 'county'
    if state == 'Alaska': extension = 'borough'
    elif state == 'Louisiana': extension = 'parish'
    elif state == 'Rhode Island': extension = 'municipality'
  
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
      try: countyName = countyName[:countyName.index('[')]
      except: pass
    
      # Skip rest of loop if retrieved name is not a county
      if countyName not in allCounties[state]: continue

      # Skip the counties of Utah - data table is too convoluted
      if state == 'Utah': continue

      # Retrieve county data
      indices = states[state]
      countyNumbers = []
      print(countyName + ', ' + state)
      for i in indices: countyNumbers.append(element.findAll('td')[i].getText(strip=True) if i > -1 else '-')

      # Add county name and data to dict
      countyData[state].update({countyName: countyNumbers})

# Dict to store all US states
states = {}
# Fill states dict with data from file
with open('locations/us-states.json') as stateFile: states = json.load(stateFile)

# Dict to store all U.S. counties
allCounties = {}
# Fill counties dict with data from file
with open('locations/us-counties.json') as countyFile: allCounties = json.load(countyFile)

# Get and store country data
countryData = {}
# getCountryData(countryData)

# Get and store county data
countyData = {}
# getStateData(countyData, states)
# getCountyData(countyData, states, allCounties)

# Write data to JSON files
# with open('data/country-data.json', 'w') as out: out.write(json.dumps(countryData, indent=2))
# with open('data/state-data.json', 'w') as out: out.write(json.dumps(countyData, indent=2))

# Dict to store email config data
config = {}
# Fill config with data from file
with open('config.json') as configFile: config = json.load(configFile)

# Create email content
message = email.message.Message()
message['Subject'] = 'test'
message['From'] = config['address']
message['To'] = config['address']
message.add_header('Content-Type', 'text/html')
message.set_payload('<h1>Hello</h1>')

# Start server and log in to sender email
server = smtplib.SMTP('smtp.gmail.com: 587')
server.starttls()
server.login(message['From'], config['password'])

# Send email and quit server
server.sendmail(message['From'], message['To'], message.as_string())
server.quit()