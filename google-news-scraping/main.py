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
from scraper import Scraper
import signal
import sys

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

def init_argparse():
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION] [FILE]...",
        description="Twitter scraper."
    )
    parser.add_argument(
        "-v", "--version", action="version",
        version = f"{parser.prog} version 1.0.0"
    )
    parser.add_argument("-t", "--ticker", dest="TICKER", required=True,
        help="Ticker of the company", metavar="string"
    )
    parser.add_argument("-n", "--ticker_name", dest="TICKER_NAME", required=True,
        help="Search query for company on Google News", metavar="string"
    )
    parser.add_argument("-d", "--directory_name", dest="DIRECTORY_NAME", required=True,
        help="Company name used for directory", metavar="string"
    )
    parser.add_argument("-w", "--chrome_webdriver_path", dest="CHROME_WEBDRIVER_PATH", required=True,
        help="Company name used for directory", metavar="string"
    )
    parser.add_argument("-e", "--environment", dest="ENVIRONMENT", required=True,
        help="Can only be 'TEST' or 'PROD'"
    )
    return parser

def setup_logging(logging):
    #if folder not created, create folder 
    now = datetime.datetime.now()
    current_date_time = now.strftime("%d%m%Y_%H%M%S.log")

    LOGS_DIR_NAME = "logs"
    LOG_FILE_NAME = current_date_time
    LOG_FILE_LOCATION = os.path.join(LOGS_DIR_NAME, LOG_FILE_NAME)

    if not os.path.exists(LOGS_DIR_NAME):
        os.makedirs(LOGS_DIR_NAME)

    logging.basicConfig(filename=LOG_FILE_LOCATION, level=logging.INFO)

def main(args):
    logging.info("Started")
    logging.info(f"Arguments - {args}")
    scraper = Scraper(args)
    
if __name__ == '__main__':
    parser = init_argparse()
    args = parser.parse_args()
    setup_logging(logging)

    if args.ENVIRONMENT == "TEST":
        main(args)
    else:
        while True:
            try:
                signal.signal(signal.SIGINT, signal_handler)
                main(args)
            except Exception as e:
                print(e)
                pass
            else:
                break

