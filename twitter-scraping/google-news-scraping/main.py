import requests
from bs4 import BeautifulSoup
import pickle 
import csv 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import datetime
import time
import argparse
import os
import matplotlib.pyplot as plt
import pandas as pd

# Variables that need to be modified by the user
ticker_name = "WBA+stock"
ticker = "WBA"
dir_name = 'WALGREEN'

  
def sentiment_scores(sentence): 
  
    sid_obj = SentimentIntensityAnalyzer() 
   
    sentiment_dict = sid_obj.polarity_scores(sentence) 
      
    print("Overall sentiment dictionary is : ", sentiment_dict) 
    print("sentence was rated as ", sentiment_dict['neg']*100, "% Negative") 
    print("sentence was rated as ", sentiment_dict['neu']*100, "% Neutral") 
    print("sentence was rated as ", sentiment_dict['pos']*100, "% Positive") 
  
    print("Sentence Overall Rated As", end = " ") 
   
    if sentiment_dict['compound'] >= 0.05 : 
        print("Positive") 
  
    elif sentiment_dict['compound'] <= - 0.05 : 
        print("Negative") 
  
    else : 
        print("Neutral") 
    return sentiment_dict['compound']


data_1 = pd.read_csv(r'dow_jones_30_daily_price.csv')
select_stocks_list = [ticker]

data_2 = data_1[data_1.tic.isin(select_stocks_list)][~data_1.datadate.isin(['20010912','20010913'])]

data_3 = data_2[['iid','datadate','tic','prccd','ajexdi']]

data_3['adjcp'] = data_3['prccd'] / data_3['ajexdi']

all_data = data_3[(data_3.datadate > 20000000) & (data_3.datadate < 20190000)]

dates = all_data['datadate'].values.tolist()

date_sentiment = dict()

date_sentiment["datadate"] = dates
date_sentiment["sentiment"] = [0 for date in dates]

query = "&tbm=nws&ei=2WlNXpSDE66W4-EPi_mtgA8&q=" + ticker_name + "&oq=" + ticker_name + "&gs_l=psy-ab.3..0l10.5670.5670.0.6280.1.1.0.0.0.0.161.161.0j1.1.0....0...1c.1.64.psy-ab..0.1.161....0._Azay032u5U"

for date in dates:

    if date<20070101:
        continue
    
    str_date = str(date)
    str_next_date = str_date
    url = "https://www.google.com/search?biw=1658&bih=948&tbs=cdr%3A1%2Ccd_min%3A" + str(str_date[4:6]) + "%2F" + str(str_date[6:]) + "%2F" + str(str_date[0:4]) + "%2Ccd_max%3A" + str(str_next_date[4:6])+ "%2F" + str(str_next_date[6:]) + "%2F" + str(str_next_date[0:4]) + query

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    pause_time = 0

    last_height = driver.execute_script("return document.body.scrollHeight")
    new_height = last_height

    start = datetime.datetime.now()

    pages=driver.find_elements_by_xpath("//*[@id='nav']/tbody/tr/td/a")
    counter=1 
    print("Num", len(pages))

    if len(pages)==0:
        pages = [0]

    hrefs = []
    for page in pages:

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(pause_time)
        link_tags = driver.find_elements_by_tag_name('a')
        for tag in link_tags:
            if "lLrAF" not in tag.get_attribute('class'):
                continue
            hrefs.append(tag.text)

        if (new_height == last_height) and (counter < len(pages)): 
            driver.find_element_by_xpath("//span[text()='Next']").click()
            counter+=1

        new_height = driver.execute_script("return document.body.scrollHeight")
        last_height = new_height

    driver.close()

    end = datetime.datetime.now()
    delta = end-start
    print("[INFO] Total time taken to scroll till the end {}".format(delta))

    if not os.path.exists(dir_name):
        try:
            os.mkdir(dir_name)
        except OSError:
            print ("[INFO] Creation of the directory {} failed".format(os.path.abspath(dir_name)))
        else:
            print ("[INFO] Successfully created the directory {} ".format(os.path.abspath(dir_name)))

    polarity = 0
    polarities = []
    for sentence in hrefs:
        p = sentiment_scores(sentence)
        polarity += p
        polarities.append(str(p))
        print(sentence + ": " + str(p))

    if len(hrefs)!=0:
        polarity = polarity/len(hrefs)

    sentiments = date_sentiment["sentiment"]

    ctr = 0
    for idate in dates:
        if idate==date:
            print("date: ", idate)
            sentiments[ctr] = polarity
            print("polarity: ", polarity)
            break
        ctr = ctr + 1
    date_sentiment["sentiment"] = sentiments

    dates_df = pd.DataFrame(date_sentiment)
    dates_df.to_csv('sentiment_' + ticker + '.csv')
