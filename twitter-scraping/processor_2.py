import datetime
import argparse
import pandas as pd
from bs4 import BeautifulSoup as bs
import csv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
import os
import re

def init_argparse():
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="Twitter HTML data processor"
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
    return parser

def processor_print(text=""):
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(f'Processor :: {current_time} :: {text}')

class Processor:
    """Will take the raw HTML pages and convert it into a CSV format for each day."""
    def __init__(self, companies='', dates=''):
        self.companies = companies
        self.dates = dates
        companies = None
        with open(self.companies, 'r') as f:
            companies = pd.read_csv(self.companies)

        if len(companies) == 0:
            sys.exit('Empty companies file detected. Please provide companies separated by newlines.')
        else:
            processor_print(f'{len(companies)} companies found')

        data = pd.read_csv(self.dates)

        dates = data['dates'].values.tolist()

        if len(dates) == 0:
            sys.exit('Empty dates file detected.')
        else:
            processor_print(f'{len(dates)} dates found. Starting on {dates[0]} and ending on {dates[-1]}.')

        for index, company in companies.iterrows(): 
            self.process_company(company['name'], dates, company['tic'])

    def process_company(self, company_name, dates, company_tic):
        processor_print(f'Starting processing {company_name}.')
        self.process_all_HTML_files(company_name, dates) # will process all Microsoft/*.html and create Microsoft/*.csv
        self.create_company_sentiment_sheet(company_name, dates, company_tic) # will create sentiment_MSFT.csv from above CSVs
        processor_print(f'Finished processing {company_name}')

    def process_all_HTML_files(self, company_name, dates):
        for date in dates[:-1]:
            filename = f'{company_name}/{str(date)}.html'
            self.process_HTML_file(filename)

    def process_HTML_file(self, filename):
        processor_print(f'Starting processing {filename}.')
        with open(filename, 'r') as f:
            raw_html = f.read()
        
        cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        cleantext = re.sub(cleanr, '', raw_html)
        cleantext = re.sub('\s+',' ',cleantext)
        
        cleantext = cleantext.strip('\t')
        cleantext = cleantext.strip('\n')

        cleantext = cleantext.replace('\n', ' ')
        tweets = cleantext.split('##########')

        tweets_data = []
        for tweet in tweets:
            if tweet=='':
                continue
            dotindex = tweet.find('·')
            useridname = tweet[:dotindex].split('@')
            
            if len(useridname)==2:
                name = useridname[0]
                handle = useridname[1]
            else:
                name = "INVALID"
                handle = "INVALID"
            tweet = tweet[dotindex+1:]

            # getting the date is very very fishy, must get better at this
            # or alternatively just fill in one of the two dates
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            for month in months:
                if tweet.find(month)!=-1:
                    dateindex= tweet.find(month)
                    date = tweet[:dateindex+3]

                    tweet_text = tweet[dotindex+4:]

                    tweet_data = {
                    'date': date,
                    'handle': handle,
                    'name': name,
                    'tweet_text': tweet_text,
                     # need to find a way to fill these up!
                    'replies': 0,
                    'retweets': 0, 
                    'favourites': 0,
                    }

                    print(date)
                    print(handle)
                    print(name)
                    print(tweet_text)
                    tweets_data.append(tweet_data)
                    break
        fields = ['date', 'handle', 'name', 'tweet_text', 'replies', 'retweets', 'favourites']  

        csv_filename = filename[:-5] + ".csv"
            
        with open(csv_filename, 'w') as csvfile:  
            writer = csv.DictWriter(csvfile, fieldnames = fields)  
            writer.writeheader()  
            writer.writerows(tweets_data) 

        processor_print(f'Created {csv_filename}')
        
        processor_print(f'Finished processing {filename}')

    def create_company_sentiment_sheet(self, company_name, dates, company_tic):
        if not os.path.exists('TwitterSentiment'):
            os.makedirs('TwitterSentiment')
        sentiments_filename = "TwitterSentiment/sentiment_" + company_tic + ".csv"
        with open(sentiments_filename, 'w') as sentiments_file:
            index = 0
            fields = ['', 'datadate', 'sentiment']  
            writer = csv.DictWriter(sentiments_file, fieldnames = fields)
            writer.writeheader() 
            sentiments = [] 
            for date in dates:
                try:
                    filename = company_name + "/" + str(date) + ".csv"
                    
                    with open(filename, mode='r') as csv_file:
                        csv_reader = csv.DictReader(csv_file)
                        line_count = 0
                        polarity = 0
                        for row in csv_reader:
                            if line_count == 0:
                                line_count += 1
                            p = self.sentiment_scores(row["tweet_text"])
                            print(f'p - {p}')
                            print(f'polarity - {polarity}')
                            polarity += p
                            line_count += 1
                        if line_count > 1:
                            polarity = polarity/(line_count - 1) #because there's a header also
                            print(f'Final polarity - {polarity}')
                    sentiment = {
                        '': index, 
                        'datadate': date,
                        'sentiment': polarity
                    }
                    sentiments.append(sentiment)
                    index += 1
                except: 
                    processor_print(f'Couldn\t processs {filename}')

            writer.writerows(sentiments)

    def sentiment_scores(self, sentence): 
        # Create a SentimentIntensityAnalyzer object. 
        sid_obj = SentimentIntensityAnalyzer() 
    
        # polarity_scores method of SentimentIntensityAnalyzer 
        # oject gives a sentiment dictionary. 
        # which contains pos, neg, neu, and compound scores. 
        sentiment_dict = sid_obj.polarity_scores(sentence) 
    
        return sentiment_dict['compound']


def main():
    processor_print("Started")
    parser = init_argparse()
    args = parser.parse_args()
    processor_print(f'Companies CSV file - {args.companies}')
    processor_print(f'Dates CSV file - {args.dates}')
    processor = Processor(args.companies, args.dates)
    
if __name__ == '__main__':
    main()
