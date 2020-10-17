import requests
from bs4 import BeautifulSoup
import pickle 
import csv 
import urllib.request 
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import datetime
import time
import argparse
import os
import matplotlib.pyplot as plt
import logging
import pandas as pd

def sentiment_scores(sentence): 
    sid_obj = SentimentIntensityAnalyzer() 
    sentiment_dict = sid_obj.polarity_scores(sentence) 
      
    logging.info(f"Overall sentiment dictionary is : {sentiment_dict}") 
    logging.info(f"sentence was rated as {sentiment_dict['neg']*100}% Negative") 
    logging.info(f"sentence was rated as {sentiment_dict['neu']*100}% Neutral") 
    logging.info(f"sentence was rated as {sentiment_dict['pos']*100} Positive") 

    if sentiment_dict['compound'] >= 0.05 : 
        logging.info("Positive") 
  
    elif sentiment_dict['compound'] <= - 0.05 : 
        logging.info("Negative") 
  
    else : 
        logging.info("Neutral") 
    return sentiment_dict['compound']

class Scraper:
    def __init__(self, args):
        self.set_environment(args)
        # dates, date_sentiment = self.load_data(start_date=20180807, end_date=20180820) #for test
        dates, date_sentiment = self.load_data()
        date_sentiment = self.scrape(dates, date_sentiment)
        # self.save_sentiment_csv(dates, date_sentiment)
        
    def set_environment(self, args):
        self.TICKER = args.TICKER
        self.TICKER_NAME = args.TICKER_NAME
        self.DIRECTORY_NAME = args.DIRECTORY_NAME
        self.CHROME_WEBDRIVER_PATH = args.CHROME_WEBDRIVER_PATH

    def load_data(self, start_date = 20000000, end_date = 20190000):
        data_1 = pd.read_csv(r'dow_jones_30_daily_price.csv')
        select_stocks_list = [self.TICKER]
        data_2 = data_1[data_1.tic.isin(select_stocks_list)][~data_1.datadate.isin(['20010912','20010913'])]
        data_3 = data_2[['iid','datadate','tic','prccd','ajexdi']]
        data_3['adjcp'] = data_3['prccd'] / data_3['ajexdi']
        all_data = data_3[(data_3.datadate > start_date) & (data_3.datadate < end_date)]
        dates = all_data['datadate'].values.tolist()
        logging.info(f"Dates - {dates}")
        date_sentiment = dict()
        date_sentiment["datadate"] = dates
        date_sentiment["sentiment"] = [0 for date in dates]
        return (dates, date_sentiment)
    
    def scrape(self, dates, date_sentiment):
        query = "&tbm=nws&ei=2WlNXpSDE66W4-EPi_mtgA8&q=" + self.TICKER_NAME + "&oq=" + self.TICKER_NAME + "&gs_l=psy-ab.3..0l10.5670.5670.0.6280.1.1.0.0.0.0.161.161.0j1.1.0....0...1c.1.64.psy-ab..0.1.161....0._Azay032u5U"
        ctr = 0
        for date in dates:
            if date<20070101:
                continue
            #check if the JSON file for that date already exists - if yes, skip processing for that day, else process that day 
            filename = os.path.join(self.DIRECTORY_NAME, str(date) + ".json")
            if (os.path.exists(filename)):
                logging.info(f"{filename} already exists.")
                continue
            else:
                str_date = str(date)
                str_next_date = str_date
                logging.info(f"Dates - {str_date} {str_next_date}")

                url = "https://www.google.com/search?biw=1658&bih=948&tbs=cdr%3A1%2Ccd_min%3A" + str(str_date[4:6]) + "%2F" + str(str_date[6:]) + "%2F" + str(str_date[0:4]) + "%2Ccd_max%3A" + str(str_next_date[4:6])+ "%2F" + str(str_next_date[6:]) + "%2F" + str(str_next_date[0:4]) + query
                logging.info(f"URL - {url}")
                options = webdriver.ChromeOptions()
                options.add_argument("--start-maximized")
                options.add_argument("--headless")

                driver = webdriver.Chrome(options=options, executable_path=self.CHROME_WEBDRIVER_PATH) 
                driver.get(url)

                pause_time = 0

                last_height = driver.execute_script("return document.body.scrollHeight")
                new_height = last_height

                pages = driver.find_elements_by_xpath("//*[@id='foot']/span/div/table/tbody/tr/td")
                pages = pages[1:len(pages)-1]
                logging.info(f"Pages - {pages}")
                counter = 1
                

                logging.info(f"Page Count - {len(pages)}")

                #check this
                if len(pages) == 0:
                    pages = [0]

                hrefs = []
                
                for page in pages:
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                    time.sleep(pause_time)
                    link_tags = driver.find_elements_by_xpath("//*[@id='rso']//a")
                    logging.info(f"Link Tags - {link_tags}")
                    for tag in link_tags:
                        logging.info(tag)
                        if (len(tag.get_attribute('class')) == 0 and (len(tag.text)!=0) and (tag.text != "Create alert") and (tag.text != "Reset search tools") and (tag.text != "Previous") and (tag.text != "Next")):
                            heading = tag.text.split("\n")[1].encode('ascii', 'ignore').decode("utf-8") 
                            logging.info(f"Heading - {heading}")
                            hrefs.append(heading)
                            logging.info(f"Sentence - {tag.text}")

                    if (new_height == last_height) and (counter < len(pages)): 
                        driver.find_element_by_xpath("//span[text()='Next']").click()
                        counter += 1

                    new_height = driver.execute_script("return document.body.scrollHeight")
                    last_height = new_height

                driver.close()
                polarity = self.calculate_polarity(hrefs)
                self.update_sentiment(ctr, date, polarity, date_sentiment)
                ctr += 1
                self.save_scraped_data(filename, hrefs, polarity, date, date_sentiment)
            
        return date_sentiment

    def update_sentiment(self, counter, date, polarity, date_sentiment):
        date_sentiment["sentiment"][counter] = polarity

    def calculate_polarity(self, sentences):
        polarity = 0
        polarities = [] 
    
        for sentence in sentences:
            p = sentiment_scores(sentence)
            polarity += p
            polarities.append(str(p))
            logging.info(f"{sentence} - {polarity}")

        if len(sentences) != 0:
            polarity = polarity/len(sentences)
        
        return polarity
    
    def save_scraped_data(self, filename, sentences, polarity, date, date_sentiment):
        if not os.path.exists(self.DIRECTORY_NAME):
            try:
                os.mkdir(self.DIRECTORY_NAME)
            except OSError:
                logging.info("Creation of the directory {} failed".format(os.path.abspath(self.DIRECTORY_NAME)))
            else:
                logging.info("Successfully created the directory {} ".format(os.path.abspath(self.DIRECTORY_NAME)))

            sentiments = date_sentiment["sentiment"]

        logging.info(f"JSON Filename - {filename}")

        ticker_headline_dict = {
            "headlines_count": len(sentences),
            "headlines": sentences,
            "polarity": polarity
        }
        logging.info(f"JSON Data - {ticker_headline_dict}")

        with open(filename, 'w') as json_file:
            headlines_obj = json.dumps(ticker_headline_dict, indent=4, sort_keys=True) #, csv_file, indent=4, sort_keys=True)
            json_file.write(headlines_obj)
            
    def save_sentiment_csv(self, dates, date_sentiment):    
        #iterate through all JSON within company directory
        #store polarity in CSV file for all dates
        counter = 0
        for date in dates: 
            json_filename = os.path.join(self.DIRECTORY_NAME, str(date) + ".json")
            if(os.path.exists(json_filename)):
                with open(json_filename) as f:
                    data = json.load(f)
                    date_sentiment['sentiment'][counter] = data['polarity']
            counter += 1

        logging.info(f"Date Sentiment - {date_sentiment}")
        dates_df = pd.DataFrame(date_sentiment)
        SENTIMENT_FILE_PATH = os.path.join(self.DIRECTORY_NAME, 'sentiment_' + self.TICKER + '.csv')
        dates_df.to_csv(SENTIMENT_FILE_PATH)
        logging.info(f"Saved Sentiment CSV - {SENTIMENT_FILE_PATH}")