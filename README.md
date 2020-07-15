# [COVID-19 Web Scraper](http://covid19reports.epizy.com/) :email:
An automated web scraper that sends you daily COVID-19 data report emails.

![Email](images/email-screenshot.jpg)

## How to sign up:
Visit [this website](http://covid19reports.epizy.com/) to sign up to receive daily COVID-19 data report emails. You will be asked to select a country and enter your name and email. If you select the United States, you may also (optionally) select a state and county.  
  
If you register twice with different selections and the same email you will receive multiple emails for each selection. If you register twice with the same sleections and same emails *you will still receive multiple emails*.  
  
Every email has an unsubscribe link at the bottom, so you can opt-out of every location you register to receive emails for.

## How it works:

*All project dependencies can be viewed in depth with the [dependency graph](https://github.com/dvptl68/covid-scraper/network/dependencies).*

Wikipedia is used for the web scraper to get COVID-19 data. It scrapes Wikipedia data table template pages, including the [worldwide data table](https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data), the [U.S. state data table](https://en.wikipedia.org/wiki/Template:COVID-19_pandemic_data/United_States_medical_cases_by_state), and a data table for every state in the U.S.
