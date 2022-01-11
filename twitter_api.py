from datetime import date
import Levenshtein
import pandas as pd
import tweepy
import json
import csv
import sys
import os

class TwitterClass:
    """
    Classe API do Twitter
    """
    def __init__(self):
        
        # path json twitter
        path_infos_json = "credenciais_twitter.json"
        path_json_flag_publicacao = "flag_publicacao.json"
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
        f = open(path_json_flag_publicacao, "r")
        infos = json.load(f)
        self.flag_publicacao = int(infos["flag_publicacao"])
        f.close()
        
        # cria lista de palavras banidas, caso não exista ainda
        if not os.path.exists(path_palavras_banidas):
            file = open(path_palavras_banidas, 'w+')
            file.close()
    
        # leitura das palavras banidas
        f = open(path_palavras_banidas, "r")
        self.lista_palavras_banidas = f.read().split('\n')
        f.close()
        
        # Autentica no Twitter
        try:
            # login API
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
            
            # Twitter API
            api = tweepy.API(auth)
            
            # Verifica credenciais
            api.verify_credentials()
            self.api = api
    
        # Erro de autenticação
        except:
            print("Erro de autenticação!")
            sys.exit(0)
        
        
        self.dict_map_emoji = {'pesca':'\U0001F3A3',
                               'peixe':'\U0001F41F',
                               'oceano':'\U0001F305',
                               'robo':'\U0001F916',
                               'surf':'\U0001F3C4',
                               'sol':'\U0001F324',
                               'sol_face':'\U0001F31E',
                               'nuvem':'\U00012601',
                               'nuvem_sol':'\U000126C5',
                               'chuva':'\U0001F327',
                               'chuva_sol':'\U0001F326',
                               'chuva_relampago':'\U000126C8',
                               'relampago':'\U00011F329',
                               'satelite':'\U0001F6F0',
                               'oculos_sol':"\U0001F60E",
                               'sombra':'\U0001F3D6',
                               'vento':'\U0001F32A',
                               'dedo_baixo':'\U0001F447',
                               'tres_pontos':'\U0001F4AC',
                               'barco_1':'\U000126F4',
                               'barco_2':'\U0001F6F3',
                               'barco_3':'\U0001F6A2',
                               'normal': '\U0001F600',
                               'sono': '\U0001F634',
                               'bravo': '\U0001F92C',
                               'covid': '\U0001F637'

                               }
        
        # limite de caracteres
        self.limite_caracteres = 280
        
        # distancia minima entre tweets
        self.distancia_minima_tweets = 0.005
        
        # limite de tweets no bd
        self.limite_tweets = 1_000_000
        
        # inicio do post
        self.inicio_post = f"{self.dict_map_emoji['robo']} "
        
        # fim do post
        self.fim_post = f"\n\n\n#AmazôniaAzul {self.dict_map_emoji['oceano']}"\
        +f"\n#redebotsdobem {self.dict_map_emoji['satelite']}"
    
    
    def valida_tweet(self, tweet):
        '''
        retorna flag indicando se o tweet é válido para ser publicados
        '''
        return self.verifica_tweet_pode_ser_publicado(tweet) and self.valida_tamanho_tweet(tweet)
        
    
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
        return self.flag_publicacao
    
    
    # publica o tweet
    def make_tweet(self, tweet, modulo, modo_operacao='padrao', tweet_id=0):
        """
        Publica um tweet utilizando a API do Twitter
        """
        tweet = self.substitui_emojis(tweet)
        print (tweet)
        try:
            if (tweet_id != 0):
                if modo_operacao == 'padrao':
                    # publica o Tweet sem foto
                    status = self.api.update_status(tweet, in_reply_to_status_id=tweet_id)

                elif modo_operacao == 'foto':
                    # publica o Tweet com foto
                    status = self.api.update_with_media("foto.png", tweet, in_reply_to_status_id=tweet_id)

                else:
                    print ('Erro! Modo de operacao nao reconhecido.')
                    sys.exit(0)
                    return 0

                # adiciona tweet ao bd
                try:
                    self.adiciona_tweet(tweet, modulo)
                except:
                    return 0

                # retorna status do tweet
                return status

            else:
                if modo_operacao == 'padrao':
                        # publica o Tweet sem foto
                        status = self.api.update_status(tweet)

                elif modo_operacao == 'foto':
                    # publica o Tweet com foto
                    status = self.api.update_with_media("foto.png", tweet)

                else:
                    print ('Erro! Modo de operacao nao reconhecido.')
                    sys.exit(0)
                    return 0

                # adiciona tweet ao bd
                try:
                    self.adiciona_tweet(tweet, modulo)
                except:
                    return 0

                # retorna status do tweet
                return status
        except Exception as e:
            return 0
                    
            
    def verifica_tweet_ok(self, tweet):
        '''
        Verifica se o tweet está ok
        '''
        try:
            # verifica se tweet possui palavras proibidas
            for palavra in self.lista_palavras_banidas:
                if palavra in tweet:
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
        for tweet_publicado in lista_tweets_publicados[:-100:-1]:
            distancia = self.calcula_distancia_strings(tweet, tweet_publicado)
            if (distancia < self.distancia_minima_tweets):
                print (f'Distancia pequena de {distancia}. Tweet vetado, muito similar.')
                return 0
        
        # tweet ok
        return 1
    
        
    def substitui_emojis(self, texto):
        '''
        substitui emoji
        '''
        lista_emojis = list(self.dict_map_emoji.keys())
        for emoji in lista_emojis:
            texto = texto.replace(f"[{emoji}]", self.dict_map_emoji[emoji])
            texto = texto.replace(f"[emoji_{emoji}]", self.dict_map_emoji[emoji])
        return texto
        
        
    def adiciona_tweet(self, tweet, modulo):
        '''
        Adiciona tweet ao bd
        '''
        
        # data de hoje
        data_hoje = date.today().strftime("%d/%m/%Y")
        
        # adiciona linha
        linha=[tweet, modulo, data_hoje]
        
        # bd atual
        df_bd = pd.read_csv('tweets_bd.csv', sep=';', encoding='utf-8')
        
        # insere linha
        df_bd.loc[-1] = linha
        df_bd.index = df_bd.index + 1
        df_bd = df_bd.sort_index()
        
        # salva bd atualizado em csv
        df_bd.to_csv('tweets_bd.csv', sep=';', index=False)