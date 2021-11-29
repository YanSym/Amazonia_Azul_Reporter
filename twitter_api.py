from datetime import date
import Levenshtein
import pandas as pd
import tweepy
import json

class Twitter_Class:
    """
    Classe API do Twitter
    """
    def __init__(self):
        
        # path json twitter
        path_infos_json = "credenciais_twitter.json"
        path_json_parametros_twitter = "parametros_twitter.json"
        path_palavras_banidas = "lista_palavras_banidas.txt"
        self.path_twitter_bd = "tweets_bd.csv"
    
        # leitura do arquivo json com as credenciais
        f = open(path_infos_json, "r")
        infos_login = json.load(f)
        CONSUMER_KEY = infos_login['CONSUMER_KEY']
        CONSUMER_SECRET = infos_login['CONSUMER_SECRET']
        ACCESS_TOKEN = infos_login['ACCESS_TOKEN']
        ACCESS_TOKEN_SECRET = infos_login['ACCESS_TOKEN_SECRET']
        f.close()
        
        # leitura do arquivo json com os parâmetros
        f = open(path_json_parametros_twitter, "r")
        infos = json.load(f)
        self.limite_caracteres = int(infos['limite_caracteres'])
        self.flag_tweet = int(infos["flag_tweet"])
        self.distancia_minima_tweets = float(infos["distancia_minima_tweets"])
        f.close()
        
        # Leitura das palavras banidas
        f = open(path_palavras_banidas, "r")
        self.lista_palavras_banidas = f.read().split('\n')
        f.close()
        
        # Autentica no Twitter
        try:
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
            
            # Tweeter API
            api = tweepy.API(auth)
            
            # Verifica credenciais
            api.verify_credentials()
            self.api = api
    
        # Erro de autenticação
        except:
            print("Erro de autenticação!")
            self.api = ''
    
    
    @staticmethod
    def calcula_distancia_strings(string1, string2):
        '''
        Retorna distância entre strings
        '''
        return (Levenshtein.distance(string1, string2)/max(len(string1), len(string2)))
    

    def get_status_twitter(self):
        '''
        Status do Twitter
        '''
        return self.flag_tweet
    
    
    # publica o tweet
    def make_tweet(self, tweet):
        """
        Publica um tweet utilizando a API do Twitter
        """
        # publica o Tweet
        self.api.update_status(tweet)
        
        # adiciona tweet ao bd
        self.adiciona_tweet(tweet)
        
        
    def verifica_tweet_ok(self, tweet):
        '''
        Verifica se o tweet está ok
        '''
        try:
            # verifica se tweet possui palavras proibidas
            for delimitador in [' ', '-', '_']:
                palavras_tweet = tweet.split(delimitador)
                for palavra in palavras_tweet:
                    if palavra in self.lista_palavras_banidas:
                        return 0
        except:
            return 0

        # tweet ok
        return 1
    
    
    def get_max_len_tweet(self):
        '''
        Retorna tamanho máximo do tweet
        '''
        return self.limite_caracteres
    

    def verifica_tweet_pode_ser_publicado(self, tweet):
        '''
        Verifica se o tweet está ok
        '''
        df_tweets = pd.read_csv(self.path_twitter_bd, sep=';').dropna(subset=['Tweet'])
        lista_tweets_publicados = df_tweets['Tweet'].values.tolist()
        
        # verifica se conteúdo já foi postado
        for tweet_publicado in lista_tweets_publicados[:100]:
            distancia = Twitter_Class.calcula_distancia_strings(tweet, tweet_publicado)
            if (distancia < self.distancia_minima_tweets):
                return 0
        
        # tweet ok
        return 1
    
        
    def adiciona_tweet(self, tweet):
        '''
        Adiciona tweet ao bd
        '''
        # conteúdo já publicado        
        lista_tweets_publicados = pd.read_csv(self.path_twitter_bd, sep=';').dropna(subset=['Tweet'])
        
        # data de hoje
        data_hoje = date.today().strftime("%d/%m/%Y")
        
        # adiciona tweet
        lista_tweets_publicados.loc[-1] = [tweet, data_hoje]
        lista_tweets_publicados.index = lista_tweets_publicados.index + 1
        lista_tweets_publicados = lista_tweets_publicados.sort_index().iloc[:10_000]
        
        # atualiza bd
        lista_tweets_publicados.to_csv(self.path_twitter_bd, index=False, sep=';')