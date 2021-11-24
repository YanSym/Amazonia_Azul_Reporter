import tweepy
import json

class Twitter_Class:
    """
    Classe API do Twitter
    """
    def __init__(self, path_infos_json="credenciais_twitter.json"):
    
        # leitura do arquivo json com as credenciais
        f = open(path_infos_json, "r")
        infos_login = json.load(f)
        CONSUMER_KEY = infos_login['CONSUMER_KEY']
        CONSUMER_SECRET = infos_login['CONSUMER_SECRET']
        ACCESS_TOKEN = infos_login['ACCESS_TOKEN']
        ACCESS_TOKEN_SECRET = infos_login['ACCESS_TOKEN_SECRET']
        f.close()
        
        # Authenticate to Twitter
        try:
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
            
            # Tweeter API
            api = tweepy.API(auth)
            
            # Verifica credenciais
            api.verify_credentials()
            self.api = api
    
        except:
            print("Erro de autenticação!")
            self.api = ''        
        

    def make_tweet(self, tweet):
        """
        Publica um tweet utilizando a APi do Twitter
        """
        # publica o Tweet
        self.api.update_status(tweet);