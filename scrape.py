import requests

url = ''
response = requests.get(url)
html = response.content
print(html)