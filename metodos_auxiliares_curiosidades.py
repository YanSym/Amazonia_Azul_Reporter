from datetime import date
import pandas as pd
import numpy as np
import random
import json
from twitter_api import TwitterClass

class CuriosidadesClass:
    """
    Classe de curiosidades
    """
    def __init__(self):
        
        # path json curiosidades
        path_json_parametros_curiosidades = "parametros_curiosidades.json"
        path_curiosidades = "curiosidades.csv"
        
        # API do Twitter
        self.twitter_api = TwitterClass()
        
        # curiosidades
        self.lista_curiosidades = pd.read_csv("curiosidades.csv", sep=';', encoding='utf-8', header=None)[0]

    
    def seleciona_curiosidade(self):
        '''
        Seleciona curiosidade da lista
        '''
        # tenta selecionar elemento aleatório da lista
        for tentativa in range(20):
            tweet = random.choice(self.lista_curiosidades)
            flag_pode_ser_publicado = self.twitter_api.verifica_tweet_pode_ser_publicado(tweet)
            if flag_pode_ser_publicado == 1:
                return 1, tweet
            
        # não encontrou curiosidades novas
        return 0, ""
    
    
    def prepara_tweet(self):
        '''
        Prepara tweet
        '''
        flag_pode_ser_publicado, curiosidade = self.seleciona_curiosidade()
        if flag_pode_ser_publicado == 0:
            return 0, ""
        
        tweet = f"{self.twitter_api.get_inicio_post()}Você sabia?\n{curiosidade}{self.twitter_api.get_fim_post()}"
        
        # verifica se tamanho está ok
        if self.twitter_api.valida_tamanho_tweet(tweet) != 1:
            return 0, ""
        
        return 1, tweet
    
    
    def publica_conteudo(self):
        '''
        Tenta publicar curiosidade
        '''
        
        # flag de publicação
        if (self.twitter_api.get_status_twitter() != 1):
            print ("Flag 0. Não posso publicar!")
            return
        
        # seleciona curiosidade para publicar
        flag, tweet = self.prepara_tweet()
        
        # tweet deu errado
        if flag == 0:
            return

        # tenta publicar 
        try:
            self.twitter_api.make_tweet(tweet)
            print ('Tweet publicado!')

        # algo deu errado
        except:
            print ('Não consegui publicar.')