from bs4 import BeautifulSoup
import requests
import json
import smtplib
import imaplib
import email.message
import mysql.connector
import os

# ALL FUNCTIONS

# Returns a bs4 object with the parsed HTML from the given URL
def getData(url): return BeautifulSoup(requests.get(url).content, 'html.parser')

# Function to scrape Wikipedia page for country data
def getCountryData(countryData):

  # Get main data table from Wikipedia main COVID-19 page
  countryTable = getData('https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data').find(id='thetable')

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
      countyData[stateName] = {'Total': list(map(lambda x: x.getText(strip=True).replace('\u2013', 'No data').replace('\u2014', 'No data'), element.findAll('td')[:3]))[:3]}

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
      for i in indices: countyNumbers.append(element.findAll('td')[i].getText(strip=True).replace('\u2013', 'No data').replace('\u2014', 'No data') if i > -1 else 'No data')

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
  with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'country-data.json'), 'w') as out: out.write(json.dumps(countryData, indent=2))
  with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'state-data.json'), 'w') as out: out.write(json.dumps(countyData, indent=2))
  with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'country-data.js'), 'w') as out: out.write(f'countries = {json.dumps(countryData, indent=2)}')
  with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'state-data.js'), 'w') as out: out.write(f'states = {json.dumps(countyData, indent=2)}')

# Function to read emails and process registrations
def processEmail(userData, config):

  # List of users to remove from database
  removeUser = []

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
        if msg.get('From') != config['name'] + ' <' + config['address'] + '>' or (subject != 'new user registration' and subject != 'remove user'): continue

        # Iterate through email parts
        for part in msg.walk():

          # Get content type of email
          content_type = part.get_content_type()

          # Get email body
          try: body = part.get_payload(decode=True).decode()
          except: continue

          # Skip rest of loop if content type is plain text
          if content_type == 'text/plain': continue

          # Add user to corresponding list
          if subject == 'new user registration':
            userData.append(json.loads(body.strip()))
          elif subject == 'remove user':
            removeUser.append(json.loads(body.strip()))

        # Send registration email to archive
        imap.store(str(i), '+FLAGS', '\\Deleted')

  # Close imap connection
  imap.expunge()
  imap.close()
  imap.logout()

  return removeUser

# Function to connect to database
def connectDB(userData, removeUser, config):

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
    command = 'INSERT INTO userData (email, name, country, state, county) VALUES (%s, %s, %s, %s, %s)'
    values = (user['email'], user['name'], user['country'], user['state'], user['county'])
    cursor.execute(command, values)
  
  # Remove users who unsubscribed
  print('Removing old data...')
  for user in removeUser: cursor.execute('DELETE FROM userData WHERE email=\'{}\' AND name=\'{}\' AND country=\'{}\' AND state=\'{}\' AND county=\'{}\''.format(user['email'], user['name'], user['country'], user['state'], user['county']))

  # Commit changes to database
  db.commit()

  # Clear userData list
  userData *= 0

  # Get all users from database
  print('Retrieving all users from database...')
  cursor.execute('SELECT * FROM userData')
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
# INSERT INTO userData (email, name, country, state, county) VALUES ('example@email.com', '', '', '', '');

# Helper function for createEmail
def calcData(new, old):
  
  try: floatNew = float(new.replace(',', ''))
  except: return new
  try: floatOld = float(old.replace(',', ''))
  except: return new

  calc = '{:.2f}'.format(((floatNew - floatOld) / floatOld) * 100)
  return f'{old} ({calc}% increase)'

# Function to create email content specific to each user
def createEmail(content, email, name, country, state, county, countryData, countyData, oldCountryData, oldCountyData):

  # Add title text
  newContent = f'<div style=\'display: inline;\'><h1 style=\'text-align: center;\'>Hello, {name}. Your daily COVID-19 report is here.</h1><p style=\'text-align: center; font-size: larger;\'>Percentage increases are calculated relative to yesterday\'s data.</p></div>'

  # Add worldwide data
  newContent += content.replace('#LOCATION#', 'Worldwide').replace('#CASES#', calcData(countryData['Total'][0], oldCountryData['Total'][0])).replace('#DEATHS#', calcData(countryData['Total'][1], oldCountryData['Total'][1])).replace('#RECOVERIES#', calcData(countryData['Total'][2], oldCountryData['Total'][2]))

  # Add country data
  newContent += content.replace('#LOCATION#', country).replace('#CASES#', calcData(countryData[country][0], oldCountryData[country][0])).replace('#DEATHS#', calcData(countryData[country][1], oldCountryData[country][1])).replace('#RECOVERIES#', calcData(countryData[country][2], oldCountryData[country][2]))

  # Return new content if state is not selected
  if state == '': return newContent

  # Add state data
  newContent += content.replace('#LOCATION#', state).replace('#CASES#', calcData(countyData[state]['Total'][0], oldCountyData[state]['Total'][0])).replace('#DEATHS#', calcData(countyData[state]['Total'][1], oldCountyData[state]['Total'][1])).replace('#RECOVERIES#', calcData(countyData[state]['Total'][2], oldCountyData[state]['Total'][2]))

  # Return new content if county is not selected
  if county == '': return newContent

  # Set correct county extension
  extension = 'county'
  if state == 'Alaska': extension = 'borough'
  elif state == 'Louisiana': extension = 'parish'
  elif state == 'Rhode Island': extension = 'municipality'

  # Add county data
  newContent += content.replace('#LOCATION#', county + ' (' + extension + '), ' + state).replace('#CASES#', calcData(countyData[state][county][0], oldCountyData[state][county][0])).replace('#DEATHS#', calcData(countyData[state][county][1], oldCountyData[state][county][1])).replace('#RECOVERIES#', calcData(countyData[state][county][2], oldCountyData[state][county][2]))

  # Add unsubscribe link
  newContent += f'<div style=\'display: inline;\'><p style=\'text-align: center; margin-top: 50px;\'><a href=\'http://covid19reports.epizy.com/php/unsubscribe.php?email={email}&name={name}&country={country}&state={state}&county={county}\'>Unsubscribe</a></p></div>'

  # Return new content
  return newContent

# Function to send an email to a recipient
def sendEmail(recipient, content, config, outcome):

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
  try:
    server.sendmail(message['From'], message['To'], message.as_string())
    outcome[0] += 1
  except Exception as e:
    print('Unable to send email to ' + recipient + '. Error: ' + str(e))
    outcome[1] += 1

  # Quit server
  server.quit()

# PROGRAM STARTS HERE

print('Retrieving required information...')

# Fill states dict with data from file
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locations', 'us-states.json')) as stateFile: states = json.load(stateFile)

# Fill counties dict with data from file
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locations', 'us-counties.json')) as countyFile: allCounties = json.load(countyFile)

# Dicts to store old and currently scraped data
oldCountryData = {}
oldCountyData = {}
countryData = {}
countyData = {}

# Get old data from files
print('Reading old data from files...')
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'country-data.json')) as read: oldCountryData = json.load(read)
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'state-data.json')) as read: oldCountyData = json.load(read)

# Scrape and store all data
scrape(countyData, countryData, states, allCounties)

# Fill config with data from file
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.json')) as configFile: config = json.load(configFile)

# List to store user data
userData = []

# Get user data from email inbox
removeUser = processEmail(userData, config)

# Add user registrations to database
connectDB(userData, removeUser, config)

# Get email HTML content
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'email.html')) as emailHTML: content = emailHTML.read()

# Send emails to users
print('Sending all emails...')
outcome = [0, 0]
for user in userData: sendEmail(user['email'], createEmail(content, user['email'], user['name'], user['country'], user['state'], user['county'], countryData, countyData, oldCountryData, oldCountyData), config, outcome)
print(f'{outcome[0]} email(s) sent, {outcome[1]} email(s) failed to send.')