import argparse
import logging
import pickle 
import pandas as pd
import threading
from datetime import datetime
import urllib
from selenium import webdriver
import datetime
import time
import argparse
import os
import matplotlib.pyplot as plt
import pandas as pd
from bs4 import BeautifulSoup as bs

def scraper_print(text=""):
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(f'Scraper :: {current_time} :: {text}')

def init_argparse():
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="Twitter scraper."
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version = f"{parser.prog} version 1.0.0"
    )
    parser.add_argument("-c", "--companies", dest="companies", required=True,
        help="CSV file with company names/keywords separated by newlines.", metavar="FILE"
    )
    parser.add_argument("-d", "--dates", dest="dates", required=True,
        help="CSV file with dates separated by newlines.", metavar="FILE"
    )
    parser.add_argument("-p", "--path", dest="path", required=True,
        help="Path to chromedriver for this scraper.", metavar="FILE"
    )
    return parser
    
class Scraper:

    def __init__(self, companies='', dates='', path=''):
        self.companies = companies
        self.dates = dates
        self.path = path
        companies = None
        with open(self.companies, 'r') as f:
            companies = pd.read_csv(self.companies)
            scraper_print(companies)

        if len(companies) == 0:
            sys.exit('Empty companies file detected. Please provide companies separated by newlines.')
        else:
            scraper_print(f'{len(companies)} companies found')

        data = pd.read_csv(self.dates)

        dates = data['dates'].values.tolist()

        if len(dates) == 0:
            sys.exit('Empty dates file detected.')
        else:
            scraper_print(f'{len(dates)} dates found. Starting on {dates[0]} and ending on {dates[-1]}.')
        
        for index, company in companies.iterrows(): 
            scraper_print(f'Starting scraping for {company["name"]} with keyword as "{company["keyword"]}"')
            next_date = current_date = None
            l = len(dates)
            directory = company["name"]

            if not os.path.exists(directory):
                os.makedirs(directory)
            
            saved_files = os.listdir('./' + directory)
            
            if len(saved_files)!=0:
                last_saved_date = saved_files[-1].split('.')[0]
                print('Found the last date saved as: ', last_saved_date)
            else:
                last_saved_date = str(dates[0])

            for index, obj in enumerate(dates):
                if str(obj)<last_saved_date:
                    print('Skipping: ', obj)
                    continue
                if index >= 0:
                    if index != l-1: #skip the last date because there's no next
                        next_date = dates[index + 1]
                        current_date = dates[index]
                        filename = f'{directory}/{current_date}.html'
                        
                        query = company.keyword + " since:" + \
                            str(current_date)[0:4] + "-" + str(current_date)[4:6] + "-" + str(current_date)[6:] \
                            + " until:" + str(next_date)[0:4] + "-" + str(next_date)[4:6] + "-" + str(next_date)[6:]

                        query = urllib.parse.quote(query)
                        search_url = "https://twitter.com/search?q=" + query 

                        options = webdriver.ChromeOptions()
                        options.add_argument('--start-maximized')
                        #options.add_argument("--headless")

                        # Initialize the Chrome webdriver and open the URL
                        driver = webdriver.Chrome(self.path, options=options)

                        scraper_print(f'Started scraping {filename}')
                        driver.get(search_url)

                        SCROLL_PAUSE_TIME = 4

                        # Get scroll height
                        last_height = driver.execute_script("return document.body.scrollHeight")
                        tweets = []
                        while True:
                            # Scroll down to bottom
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                            # Wait to load page
                            time.sleep(SCROLL_PAUSE_TIME)

                            # Calculate new scroll height and compare with last scroll height
                            new_height = driver.execute_script("return document.body.scrollHeight")
                            # print(driver.page_source) 
                            # with open(filename, 'a') as f:
                            new_tweets = driver.find_elements_by_tag_name('article')
                            for new_tweet in new_tweets:
                                tweets.append(new_tweet.get_attribute('outerHTML'))
                            
                            if new_height == last_height:
                                new_tweets = driver.find_elements_by_tag_name('article')
                                for new_tweet in new_tweets:
                                    tweets.append(new_tweet.get_attribute('outerHTML'))

                                with open(filename, 'w', encoding="utf-8") as f:
                                    tweets = list(dict.fromkeys(tweets))
                                    print(f'Number of tweets - {len(tweets)}')
                                    for tweet in tweets:
                                        f.write(tweet)
                                        f.write("##########")
                                break
                            last_height = new_height

                        scraper_print(f'Finished scraping {filename}')
                        driver.close()
            scraper_print(f'Finished scraping for {company["name"]} with keyword as "{company["keyword"]}"')   

def main():
    scraper_print("Started")
    parser = init_argparse()
    args = parser.parse_args()
    scraper_print(f'Companies CSV file - {args.companies}')
    scraper_print(f'Dates CSV file - {args.dates}')
    scraper = Scraper(args.companies, args.dates, args.path)
    
if __name__ == '__main__':
    while True:
        try:
            main()
        except:
            pass
        else:
            break

