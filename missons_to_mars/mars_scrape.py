
from bs4 import BeautifulSoup as bs
from webdriver_manager.chrome import ChromeDriverManager
from splinter import Browser
import pandas as pd
import time


def scrape():

    # First we go to the redplanetscience site and get the news titles

    target_site = "https://redplanetscience.com/"

    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    # In case this code runs into a problem, we want to make sure we still close the browser, so we use try/except/finally  

    try:
        browser.visit(target_site)
        html = browser.html
        soup = bs(html, 'html.parser')

        # I sometimes ran into an error when the page didn't load immediately, so we sleep for 5 seconds
        # The rest of them we'll only sleep for 1 second since it doesn't seem to need to load as much

        time.sleep(5)

        # We're interested only in the first (most recent) piece of content so we can use .find here
        news_title = soup.find('div', class_='content_title').text
        news_p = soup.find('div', class_='article_teaser_body').text


        # Next up is spaceimages

        target_site = "https://spaceimages-mars.com/"

        browser.visit(target_site)
        html = browser.html
        soup = bs(html, 'html.parser')

        time.sleep(1)

        featured_image_url = soup.find('a', class_='showimg fancybox-thumbs')['href']

        # Now for mars facts

        target_site = "https://galaxyfacts-mars.com/"

        browser.visit(target_site)
        html = browser.html
        soup = bs(html, 'html.parser')

        time.sleep(1)

        tables = pd.read_html(target_site)

        # pd.read_html gives us a list of 2 tables, the first one is comparing earth and mars, we want the second one 
        mars_facts = tables[1]
    
        # Now to get the images of the martian hemispheres
    
        target_site = "https://marshemispheres.com/"
    
        browser.visit(target_site)
        html = browser.html
        soup = bs(html, 'html.parser')

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
            image_link = browser.links.find_by_text("Original")['href']
    
            # Then we make a dictionary to hold what we found and append it to the hemisphere_image_urls
            image_dict = {"title":link, "img_url":image_link}
            hemisphere_image_urls.append(image_dict)
    
            time.sleep(1)
            browser.back()
            time.sleep(1)
    
    except:
        print("Something went wrong")
    
    finally:
        browser.quit()

    return news_title, news_p, featured_image_url, mars_facts, hemisphere_image_urls