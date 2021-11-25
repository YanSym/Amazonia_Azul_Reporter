import tweepy
import json

class Twitter_Class:
    """
    Classe API do Twitter
    """
    def __init__(self):
        
        # path json twitter
        path_infos_json="credenciais_twitter.json"
    
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
        
        
    def verifica_tweet_ok(tweet):
        '''
        Verifica se o tweet está ok
        '''
        # Leitura das palavras banidas
        f = open("lista_palavras_banidas.txt", "r")
        lista_palavras_banidas = f.read().split('\n')
        f.close()
        
        # verifica se tweet possui palavras proibidas
        for delimitador in [' ', '-', '_']:
            palavras_tweet = tweet.split(delimitador)
            for palavra in palavras_tweet:
                if palavra in lista_palavras_banidas:
                    return 0

        # tweet ok
        return 1