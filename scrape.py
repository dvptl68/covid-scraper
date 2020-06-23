import requests
from bs4 import BeautifulSoup

def getData(url): return BeautifulSoup(requests.get(url).content, 'html.parser')

url = 'https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data'
print(getData(url).prettify())
