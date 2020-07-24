# Mission to Mars web scraping app calling on news, images, weather, facts, and hemisphere information for Mars
from bs4 import BeautifulSoup
import requests
import pymongo
from splinter import Browser
import pandas as pd
import time
import re

# Initialize PyMongo to work with MongoDBs
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

def init_browser():
    
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

def scrape():
    browser = init_browser()

    #Retrieve NASA Mars News
   
    NASA_url = 'https://mars.nasa.gov/news/'

    Marsnews = requests.get(NASA_url)

    NASA_soup = BeautifulSoup(Marsnews.text, 'html.parser')

    newsstory = NASA_soup.find('div', class_='slide')

    #Latest Mars News Story Title
    newstitle = newsstory.find('div', class_='content_title').find('a').text.strip()
    #Latest Mars News Story Blurb
    newscontent = newsstory.find('div', class_='rollover_description_inner').text.strip()


    #Retrieve JPL Mars Space Featured Image
    jplurl = 'https://www.jpl.nasa.gov/'
    browser.visit(jplurl)
    time.sleep(5)
    jplhtml = browser.html
    
    jplsoup = BeautifulSoup(jplhtml, 'html.parser')

    image = jplsoup.find('article', class_='slide-1')
    #Featured Image URL
    featuredurl = image.img['src']


    #Retrieve Mars Weather information
    weatherurl = 'https://twitter.com/marswxreport?lang=en'

    browser.visit(weatherurl)

    time.sleep(5)

    weatherhtml = browser.html

    #Latest Mars weather information
    weather = re.findall(r'(InSight sol [\d]{3} \([\d]{4}-[\d]{2}-[\d]{2}\) low -[\d]{1,3}\.\d.C \(-[\d]{1,3}.\d.F\) high -[\d]{1,3}.\d.C \([\d]{1,3}\.\d.F\)\nwinds from the [\w]{1,3} at [\d]{1,3}\.\d m/s \([\d]{1,3}\.\d mph\) gusting to [\d]{1,3}\.\d m/s \([\d]{1,3}\.\d mph\)\npressure at [\d]{1,3}\.[\d]{2} hPa)', weatherhtml)
    marsweather = weather[0]

    #Retrieve Mars Facts
    factsurl = 'https://space-facts.com/mars/'

    tables = pd.read_html(factsurl)

    Marsdf = tables[0]
    Marsdf.set_index([0])
    Marsdf = Marsdf.rename(columns={0:'', 1:'Measurement'})
    Marsdf.set_index([""], inplace=True)
    Marstable = Marsdf.to_html(classes='table table-borderless table-hover table-dark')

    #Retrieve Mars Hemisphere data
    hemisurls = []

    hem_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hem_url)
    time.sleep(5)
    hem_html = browser.html
    hem_soup = BeautifulSoup(hem_html, 'html.parser')
    tag = list(hem_soup.find_all('h3'))

    for x in range(0,4):
        browser.find_by_text(tag[x].text.strip()).click()
    
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
    
       
        image = soup.find('div', class_='downloads').find('ul').find('li')
        image_url = image.find('a')
        title = soup.find('h2', class_='title')
    

        hem_url.append({'title':title.text.strip(), 'image_url':image_url["href"]})
    
        browser.back()

    Mars_data = {'News':[news_title,
                        news_content],
                'Image': featured_url,
                'Weather': mars_weather,
                'Facts': Mars_table,
                'Hemispheres': hemisphere_image_urls}


    # Close the browser after scraping
    browser.quit()
    
                
    return Mars_data