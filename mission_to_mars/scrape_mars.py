from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
from splinter import Browser
import pandas as pd
import time

import traceback


def scrape():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    # We create a dictionary to store all of our results.
    mission_to_mars = {}

    # In case this code runs into a problem, we want to make sure we still close the browser, so we use try/except/finally  
    try:
        target_site = "https://redplanetscience.com/"

        browser.visit(target_site)
        html = browser.html
        soup = bs(html, 'html.parser')

        # I sometimes ran into an error when the page didn't load immediately, so we sleep for 5 seconds
        # The rest of them we'll only sleep for 1 second since it doesn't seem to need to load as much

        time.sleep(5)

        # We're interested only in the first (most recent) piece of content so we can use .find here
        news_title = soup.find('div', class_='content_title').text
        news_p = soup.find('div', class_='article_teaser_body').text

        mission_to_mars["headline"] = news_title
        mission_to_mars["news"] = news_p


        # Next up is spaceimages

        target_site = "https://spaceimages-mars.com/"

        browser.visit(target_site)
        html = browser.html
        soup = bs(html, 'html.parser')

        time.sleep(1)

        featured_image_url = soup.find('a', class_='showimg fancybox-thumbs')['href']

        mission_to_mars["featured"] = target_site + featured_image_url

        

        # Now for mars facts

        target_site = "https://galaxyfacts-mars.com/"
        browser.visit(target_site)
        html = browser.html
        soup = bs(html, 'html.parser')

        time.sleep(1)

        tables = pd.read_html(target_site)

        # pd.read_html gives us a list of 2 tables, the first one is comparing earth and mars 
        mars_facts = tables[0]

        # Using panda's .to_html method we format the table so that it looks better in the finished index.html
        mission_to_mars["facts"] = mars_facts.to_html(index=False, header=False, classes="col table table-striped", table_id="mars_facts", border=5, escape=False)
    
        # Now to get the images of the martian hemispheres
    
        target_site = "https://marshemispheres.com/"
    
        browser.visit(target_site)
        html = browser.html
        soup = bs(html, 'html.parser')

        time.sleep(1)

        # This gets a list of links in the web page and adds them to a list, excluding the back link
        links = []

        for link in soup.find_all('h3'):
            link_address = link.text
            if link_address not in links:
                links.append(link_address)

        # We take out the back button
        links.remove("Back")

        hemisphere_image_urls = []

        # Looping through the list we have we click on each link taking us to the next page,
        # then find the button labeled original to get the link for that

        for link in links:
            browser.find_by_css('h3').links.find_by_partial_text(link).click()
            image_link = browser.links.find_by_text("Sample")['href']
    
            # All of our links end with the word "Enhanced" which we don't really want in the finished name
            hemisphere_name = link.replace(" Enhanced", "")

            # Then we make a dictionary to hold what we found and append it to the hemisphere_image_urls
            image_dict = {"title":hemisphere_name, "img_url":image_link}
            hemisphere_image_urls.append(image_dict)
    
            time.sleep(1)
            browser.back()
            time.sleep(1)

        mission_to_mars["images"] = hemisphere_image_urls
    
    except Exception:

        # If an exception occurs we still want to know what went wrong
        print(traceback.format_exc())
    
    finally:

        # Whether the code completes without error or not, we want to make sure the browser is closed
        browser.quit()
    
    
    return mission_to_mars