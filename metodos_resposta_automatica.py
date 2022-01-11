import pandas as pd
import numpy as np
import requests
import random
import heapq
import nltk
import json
import sys
import re
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from twitter_api import TwitterClass


class RespostaClass:
    """
    Classe de métodos auxiliares
    """
    def __init__(self):
        
        
        # API do Twitter
        self.twitter_api = TwitterClass()
    

    def responde_conteudo(self):
        aa
    
    
def check_mentions(api, keywords, since_id):
    logging.info("Retrieving mentions")
    new_since_id = since_id
    for tweet in tweepy.Cursor(api.mentions_timeline,
        since_id=since_id).items():
        new_since_id = max(tweet.id, new_since_id)
        if tweet.in_reply_to_status_id is not None:
            continue
        if any(keyword in tweet.text.lower() for keyword in keywords):
            logging.info(f"Answering to {tweet.user.name}")

            if not tweet.user.following:
                tweet.user.follow()

            api.update_status(
                status="Please reach us via DM",
                in_reply_to_status_id=tweet.id,
            )
    return new_since_id

def main():
    api = create_api()
    since_id = 1
    while True:
        since_id = check_mentions(api, ["help", "support"], since_id)
        time.sleep(10)

if __name__ == "__main__":
    main()