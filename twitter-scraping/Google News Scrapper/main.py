import requests
from bs4 import BeautifulSoup
import pickle 
import csv 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
  
def sentiment_scores(sentence): 
  
    # Create a SentimentIntensityAnalyzer object. 
    sid_obj = SentimentIntensityAnalyzer() 
  
    # polarity_scores method of SentimentIntensityAnalyzer 
    # oject gives a sentiment dictionary. 
    # which contains pos, neg, neu, and compound scores. 
    sentiment_dict = sid_obj.polarity_scores(sentence) 
      
    print("Overall sentiment dictionary is : ", sentiment_dict) 
    print("sentence was rated as ", sentiment_dict['neg']*100, "% Negative") 
    print("sentence was rated as ", sentiment_dict['neu']*100, "% Neutral") 
    print("sentence was rated as ", sentiment_dict['pos']*100, "% Positive") 
  
    print("Sentence Overall Rated As", end = " ") 
  
    # decide sentiment as positive, negative and neutral 
    if sentiment_dict['compound'] >= 0.05 : 
        print("Positive") 
  
    elif sentiment_dict['compound'] <= - 0.05 : 
        print("Negative") 
  
    else : 
        print("Neutral") 
    return sentiment_dict['compound']
  
# # field names 
# fields = ['Date', 'Sentiment Score'] 
  
  
# # name of csv file 
# filename = "sentiment_scores.csv"

# rows = []
  
# # writing to csv file 
# with open(filename, 'w') as csvfile: 
#     # creating a csv writer object 
#     csvwriter = csv.writer(csvfile) 
      
#     # writing the fields 
#     csvwriter.writerow(fields) 
#     with open("karan_dates.txt", "rb") as fp:
#         mydates = pickle.load(fp)
#         i = 1
#         for date in mydates[:1]:
#             str_date = str(date)[:4] + "-" + str(date)[4:6] + "-"  + str(date)[6:]
#             str_next_date = str(mydates[i])[:4] + "-" + str(mydates[i])[4:6] + "-"  + str(mydates[i])[6:]
#             str_date = "20190125"
#             str_next_date = "20190127"
#             print(date)
#             print(str_next_date)
#             # url = "https://www.google.com/search?q=Apple after:" + str_date + " before:" + str_next_date + "&tbm=nws&source=lnt&sa=X&bih=948&dpr=2"
#             # url = "https://www.google.com/search?biw=1658&bih=948&tbs=cdr%3A1%2Ccd_min%3A" + str(str_date[4:6]) + "%2F" + str(str_date[6:]) + "%2F" + str(str_date[0:4]) + "%2Ccd_max%3A" + str(str_next_date[4:6])+ "%2F" + str(str_next_date[6:]) + "%2F" + str(str_next_date[0:4]) + "&tbm=nws&ei=2WlNXpSDE66W4-EPi_mtgA8&q=Apple&oq=Apple&gs_l=psy-ab.3..0l10.5670.5670.0.6280.1.1.0.0.0.0.161.161.0j1.1.0....0...1c.1.64.psy-ab..0.1.161....0._Azay032u5U"
#             print(url)
#             result = requests.get(url)
#             src = result.content
#             soup = BeautifulSoup(src, 'lxml')
#             # print(soup)
#             texts = soup.find_all("div", class_="s3v9rd")
#             # # print(texts)
#             count = 0
#             sentiment_score = 0
#             for text in texts:
#                 sentiment_score = sentiment_score + sentiment_scores(text.text)
#                 print(text.text)
#                 count = count + 1
            
#             # sentiment_score = sentiment_score/count

#             # links = soup.find_all("a")
#             # count = 0
#             # sentiment_score2 = 0
            
#             # for link in links:
#             #     print(link.text)
#             # for link in links[18:-5]:
#             #     i = 0
#             #     for child in link.children:
#             #         print(child.text)
#             #         sentiment_score2 = sentiment_score2 + sentiment_scores(child.text)
#             #         count = count + 1
#             #         if (i == 0):
#             #             break

#             # sentiment_score2 = sentiment_score2/count

#             # # sentiment_score = (sentiment_score + sentiment_score2)/2

#             # print(sentiment_score2)
#                 # print(link.text)
#             # links = soup.find_all("a")
#             # for link in links:
#             #     print(link)
#             # # if 'forbes' in link.attrs['href']:
#             # # print(link.attrs['href'])
#             # i = i + 1
        
#         # writing the data rows 
#         # csvwriter.writerows(rows)


# # print(len(links))


from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import datetime
import time
import argparse
import os
import matplotlib.pyplot as plt
import pandas as pd


#Define the argument parser to read in the URL
# parser = argparse.ArgumentParser()
# parser.add_argument('-url', '--url', help='URL to the online repository of images')
# args = vars(parser.parse_args())
# url = args['url']


data_1 = pd.read_csv(r'C:\Users\Mridul\myenv\Lib\site-packages\gym\envs\zxstock\Data_Daily_Stock_Dow_Jones_30\dow_jones_30_daily_price.csv')
select_stocks_list = ['WBA']

data_2 = data_1[data_1.tic.isin(select_stocks_list)][~data_1.datadate.isin(['20010912','20010913'])]

data_3 = data_2[['iid','datadate','tic','prccd','ajexdi']]

data_3['adjcp'] = data_3['prccd'] / data_3['ajexdi']

all_data = data_3[(data_3.datadate > 20000000) & (data_3.datadate < 20190000)]

dates = all_data['datadate'].values.tolist()

date_sentiment = dict()

date_sentiment["datadate"] = dates
date_sentiment["sentiment"] = [0 for date in dates]

for date in dates:

    if date<20070101:
        continue
    
    str_date = str(date)
    str_next_date = str_date
    url = "https://www.google.com/search?biw=1658&bih=948&tbs=cdr%3A1%2Ccd_min%3A" + str(str_date[4:6]) + "%2F" + str(str_date[6:]) + "%2F" + str(str_date[0:4]) + "%2Ccd_max%3A" + str(str_next_date[4:6])+ "%2F" + str(str_next_date[6:]) + "%2F" + str(str_next_date[0:4]) + "&tbm=nws&ei=2WlNXpSDE66W4-EPi_mtgA8&q=WBA+stock&oq=WBA+stock&gs_l=psy-ab.3..0l10.5670.5670.0.6280.1.1.0.0.0.0.161.161.0j1.1.0....0...1c.1.64.psy-ab..0.1.161....0._Azay032u5U"

    # Extract the album name
    album_name = 'WALGREENS'

    # Define Chrome options to open the window in maximized mode
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")

    # Initialize the Chrome webdriver and open the URL
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Define a pause time in between scrolls
    pause_time = 0

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    new_height = last_height
    # Record the starting time
    start = datetime.datetime.now()

    pages=driver.find_elements_by_xpath("//*[@id='nav']/tbody/tr/td/a")
    counter=1  #starting from 2
    print("Num", len(pages))

    if len(pages)==0:
        pages = [0]

    hrefs = []
    for page in pages:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # wait to load page
        time.sleep(pause_time)
        link_tags = driver.find_elements_by_tag_name('a')
        for tag in link_tags:
            if "lLrAF" not in tag.get_attribute('class'):
                continue
            hrefs.append(tag.text)
        # Calculate new scroll height and compare with last scroll height
        if (new_height == last_height) and (counter < len(pages)): # which means end of page
            driver.find_element_by_xpath("//span[text()='Next']").click()
            counter+=1
        # update the last height
        new_height = driver.execute_script("return document.body.scrollHeight")
        last_height = new_height

    driver.close()

    # Record the end time, then calculate and print the total time
    end = datetime.datetime.now()
    delta = end-start
    print("[INFO] Total time taken to scroll till the end {}".format(delta))

    # # Extract all anchor tags
    # link_tags = driver.find_elements_by_tag_name('a')

    # # Create an emply list to hold all the urls for the images
    # hrefs = []
    # # print(link_tags)
    # # Extract the urls of only the images from each of the tag WebElements
    # # print(dir(link_tags[0]))
    # for tag in link_tags:
    #     # print(tag.get_attribute('class'))
    #     # print(tag.text)
    #     # print('\n')
    #     if "lLrAF" not in tag.get_attribute('class'):
    #         continue
    #     hrefs.append(tag.text)

    #Create the directory after checking if it already exists or not
    dir_name = 'WALGREENS'
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
    # Write the links to the image pages to a file
    # f = open("{}/{}.csv".format(dir_name, album_name),'w')
    # f.write(",\n".join(hrefs))
    # f.write(",\n".join(polarities))
    # f.write(",\n")
    # f.write(str(polarity))
    # print ("[INFO] Successfully created the file {}.csv with {} links".format(album_name, len(hrefs)))

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
    dates_df.to_csv('sentiments.csv')