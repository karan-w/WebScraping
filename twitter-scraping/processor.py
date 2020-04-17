import datetime
import argparse
import pandas as pd
from bs4 import BeautifulSoup as bs

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
            self.process_company(company['name'], dates)

    def process_company(self, company_name, dates):
        processor_print(f'Starting processing {company_name}.')
        # for date in dates[:-1]:
        #     filename = f'{company_name}/{str(date)}.html'
        #     self.process_HTML_file(filename)

        filename = f'{company_name}/{str(dates[0])}.html'
        self.process_HTML_file(filename)
        
        processor_print(f'Finished processing {company_name}')

    def process_HTML_file(self, filename):
        processor_print(f'Starting processing {filename}.')
        with open(filename, 'r') as f:
            html = f.read()
        soup = bs(html, features="lxml")               
        articles = soup.find_all('article')
        article = articles[0]
        article = article.find(attrs={"data-testid":"tweet"})
        tweet = article.contents[3]
        # author = tweet.find

        # for content in article.contents:
        #     print("CONTENT---------------------------")
            # print(content)
        
        # spans = article.find_all('span', 'css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0')
        # print(spans.text)
        # links = article.find_all('a')
        # print(links)
        # for link in links:
        #     print(link)
        # print(article.children[0])
        # print(article)
        # for child in article.children:
        #     print(child)
        # for article in articles:   
        #     print(article.get_text())
        processor_print(f'Finished processing {filename}')
    # def process_all_CSV(self):
        


def main():
    processor_print("Started")
    parser = init_argparse()
    args = parser.parse_args()
    processor_print(f'Companies CSV file - {args.companies}')
    processor_print(f'Dates CSV file - {args.dates}')
    processor = Processor(args.companies, args.dates)
    
if __name__ == '__main__':
    main()
