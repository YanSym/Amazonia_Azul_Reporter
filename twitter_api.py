from datetime import date
import Levenshtein
import pandas as pd
import tweepy
import json

class TwitterClass:
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
        
        
        self.dict_map_emoji = {'pesca':'\U0001F3A3',
                               'peixe':'\U0001F41F',
                               'oceano':'\U0001F305',
                               'robo':'\U0001F916',
                               'surf':'\U0001F3C4',
                               'sol':'\U0001F324',
                               'sol_face':'\U0001F31E',
                               'chuva':'\U0001F327',
                               'chuva_sol':'\U0001F326',
                               'chuva_relampago':'\U000126C8',
                               'relampago':'\U00011F329',
                               'satelite':'\U0001F6F0',
                               'oculos_sol':"\U0001F60E",
                               'sombra':'\U0001F3D6',
                               'vento':'\U0001F32A'
                               }
        
        # inicio do post
        self.inicio_post = f"{self.dict_map_emoji['robo']} "
        
        # fim do post
        self.fim_post = f"\n\n\n#AmazôniaAzul {self.dict_map_emoji['oceano']}"\
        +f"\n#redebotsdobem {self.dict_map_emoji['satelite']}"
    
    
    def calcula_distancia_strings(self, string1, string2):
        '''
        Retorna distância entre strings
        '''
        return (Levenshtein.distance(string1, string2)/max(len(string1), len(string2)))
    
    
    def valida_tamanho_tweet(self, tweet):
        '''
        valida tamanho do tweet
        retorna True caso menor e False caso maior que o limite de caracteres
        '''
        flag = (len(tweet) <= self.limite_caracteres)
        return flag
    
    
    def get_inicio_post(self):
        '''
        retorna fim do post
        '''
        return self.inicio_post
    
    
    def get_fim_post(self):
        '''
        retorna fim do post
        '''
        return self.fim_post
    

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
    

    def verifica_tweet_pode_ser_publicado(self, tweet):
        '''
        Verifica se o tweet está ok
        '''
        df_tweets = pd.read_csv(self.path_twitter_bd, sep=';').dropna(subset=['Tweet'])
        lista_tweets_publicados = df_tweets['Tweet'].values.tolist()
        
        # verifica se conteúdo já foi postado
        for tweet_publicado in lista_tweets_publicados[:100]:
            distancia = self.calcula_distancia_strings(tweet, tweet_publicado)
            if (distancia < self.distancia_minima_tweets):
                print (f'Distancia pequena de {distancia}. Tweet vetado, muito similar.')
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