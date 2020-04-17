import datetime
import argparse
import pandas as pd
from bs4 import BeautifulSoup as bs
import csv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 
import os

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
            html = f.read()
        soup = bs(html, features="lxml")               
        articles = soup.find_all('article')
        tweets_data = []
        for article in articles:
            try:
                article = article.find(attrs={"data-testid":"tweet"})
                tweet = article.contents[len(article) - 1]
                date = tweet.find('a', 'css-4rbku5 css-18t94o4 css-901oao r-1re7ezh r-1loqt21 r-1q142lx r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-3s2u2q r-qvutc0')
                date = date.text
                authors = tweet.find_all('span', 'css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0')
                handle = authors[2]
                handle = handle.text
                name = authors[1]
                name = name.text
                replies = authors[-3]
                replies = replies.text
                retweets = authors[-2]
                retweets = retweets.text
                favourites = authors[-1]
                favourites = favourites.text
                text = tweet.find('div', 'css-901oao r-hkyrab r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0')
                text = text.text
                text = text.strip('\n')
                text = text.strip('\t')
                print(type(replies))
                print(replies)
                tweet_data = {
                    'date': date,
                    'handle': handle,
                    'name': name,
                    'tweet_text': text,
                    'replies': int(replies.replace(" ", "")),
                    'retweets': int(retweets.replace(" ", "")), 
                    'favourites': int(favourites.replace(" ", "")),
                }
            except: 
                tweet_data = {
                    'date': "",
                    'handle': "",
                    'name': "",
                    'tweet_text': "",
                    'replies': 0,
                    'retweets': 0, 
                    'favourites': 0,
                }

            tweets_data.append(tweet_data)
            
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
