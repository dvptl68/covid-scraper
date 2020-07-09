from bs4 import BeautifulSoup
import requests
import json
import smtplib
import imaplib
import email.message
import mysql.connector

# ALL FUNCTIONS

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
      # print(countyName + ', ' + state)
      for i in indices: countyNumbers.append(element.findAll('td')[i].getText(strip=True) if i > -1 else '-')

      # Add county name and data to dict
      countyData[state].update({countyName: countyNumbers})

# Function to scrape all data and store in files
def scrape(countyData, countryData, states, allCounties):

  # Scrape all data
  print('Retrieving country data...')
  getCountryData(countryData)

  print('Retrieving state data...')
  getStateData(countyData, states)

  print('Retrieving county data...')
  getCountyData(countyData, states, allCounties)

  # Write data to JSON files
  print('Writing data to files...')
  with open('data/country-data.json', 'w') as out: out.write(json.dumps(countryData, indent=2))
  with open('data/state-data.json', 'w') as out: out.write(json.dumps(countyData, indent=2))

# Function to read emails and process registrations
def processEmail(userData, config):

  # Log in to email account and select inbox
  print('Logging into email to read...')
  imap = imaplib.IMAP4_SSL('imap.gmail.com')
  imap.login(config['address'], config['password'])
  status, messages = imap.select('INBOX')
  messages = int(messages[0])

  # Iterate through all emails in inbox
  print('Reading all emails...')
  for i in range(messages, 0, -1):

    # Get message ID
    res, msg = imap.fetch(str(i), '(RFC822)')

    for response in msg:

      if isinstance(response, tuple):

        msg = email.message_from_bytes(response[1])

        # Decode email subject
        subject = email.header.decode_header(msg['Subject'])[0][0]

        # Decode subject if it is byte code
        if isinstance(subject, bytes): subject = subject.decode()

        # Skip rest of loop if email is not from correct sender and not about new user registration
        if msg.get('From') != config['name'] + ' <' + config['address'] + '>' or subject != 'new user registration': continue

        # Iterate through email parts
        for part in msg.walk():

          # Get content type of email
          content_type = part.get_content_type()

          # Get email body
          try: body = part.get_payload(decode=True).decode()
          except: pass

          # Add data if content type is plain text
          if content_type == 'text/plain': userData.append(json.loads(body.strip()))

        # Send registration email to archive
        imap.store(str(i), '+FLAGS', '\\Deleted')

  # Close imap connection
  imap.expunge()
  imap.close()
  imap.logout()

# Function to connect to database
def connectDB(userData, config):

  # Establish connection
  print('Connecting to database...')
  db = mysql.connector.connect(
    host = config['db']['host'],
    user = config['db']['user'],
    password = config['db']['password'],
    database = config['db']['database']
  )

  # Set database cursor
  cursor = db.cursor()

  # Insert user data into database for each user
  print('Writing new data to database...')
  for user in userData:
    command = 'INSERT INTO ' + config['db']['tableName'] + ' (email, name, country, state, county) VALUES (%s, %s, %s, %s, %s)'
    values = (user['email'], user['name'], user['country'], user['state'], user['county'])
    cursor.execute(command, values)

  # Commit changes to database
  db.commit()

  # Clear userData list
  userData *= 0

  # Get all users from database
  print('Retrieving all users from database...')
  cursor.execute('SELECT * FROM ' + config['db']['tableName'])
  result = cursor.fetchall()
  for user in result:
    userData.append({
      'email': user[1],
      'name': user[2],
      'country': user[3],
      'state': user[4],
      'county': user[5]
    })

  # CLose connections
  cursor.close()
  db.close()

# CREATE TABLE userData (id INT AUTO_INCREMENT PRIMARY KEY, email TEXT NOT NULL, name TEXT NOT NULL, country TEXT NOT NULL, state TEXT, county TEXT);
# INSERT INTO userData (email, name, country, state, county) VALUES ('inferno686868@gmail.com', 'nick', 'sda', 'sdaw', 'sdaw');

# Function ot create email content specific to each user
def createEmail(content, name, country, state, county, countryData, countyData):

  # Add HTML opening tags
  newContent = '<!DOCTYPE html><html><head></head><body>'

  # Add title text
  newContent += '<div style=\'position: absolute; width: 100%; top: 0; left: 0;\'>'
  newContent += f'<h1 style=\'text-align: center;\'>Hello, {name}. Your daily COVID-19 report is here.</h1></div>'

  # Add worldwide data
  newContent += content.replace('#LOCATION#', 'Worldwide').replace('#CASES#', countryData['Total'][0]).replace('#DEATHS#', countryData['Total'][1]).replace('#RECOVERIES#', countryData['Total'][2])

  # Add country data
  newContent += content.replace('#LOCATION#', 'Worldwide').replace('#CASES#', countryData[country][0]).replace('#DEATHS#', countryData[country][1]).replace('#RECOVERIES#', countryData[country][2])

  # Add closing tags and return new content if state is not selected
  if state == '': return newContent + '</body></html>'


  # Add closing tags and return new content if county is not selected
  if county == '': return newContent + '</body></html>'

  # Return new content with closing tags
  return newContent + '</body></html>'

# Function to send an email to a recipient
def sendEmail(recipient, content, config):

  # Create email content
  message = email.message.Message()
  message['Subject'] = 'Your daily COVID-19 report'
  message['From'] = config['address']
  message['To'] = recipient
  message.add_header('Content-Type', 'text/html')
  message.set_payload(content)

  # Start server and log in to sender email
  server = smtplib.SMTP('smtp.gmail.com: 587')
  server.starttls()
  server.login(message['From'], config['password'])

  # Attempt to send email
  try: server.sendmail(message['From'], message['To'], message.as_string())
  except: print('Unable to send email to ' + recipient)

  # Quit server
  server.quit()

# PROGRAM STARTS

print('Retrieving required information...')

# Fill states dict with data from file
with open('locations/us-states.json') as stateFile: states = json.load(stateFile)

# Fill counties dict with data from file
with open('locations/us-counties.json') as countyFile: allCounties = json.load(countyFile)

# Dicts to store scraped data
countryData = {}
countyData = {}

# Scrape and store all data
scrape(countyData, countryData, states, allCounties)

# Fill config with data from file
with open('config.json') as configFile: config = json.load(configFile)

# List to store user data
userData = []

# Get user data from email inbox
# processEmail(userData, config)

# Add user registrations to database
# connectDB(userData, config)

# Get email HTML content
with open('email.html') as emailHTML: content = emailHTML.read()

# Send emails to users
print('Sending all emails...')
for user in userData: sendEmail(user['email'], createEmail(content, user['name'], user['country'], user['state'], user['county'], countryData, countyData), config)

print('Done!')