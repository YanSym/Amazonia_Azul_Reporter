from datetime import date
import pandas as pd
import numpy as np
import random
import json
import sys
from twitter_api import TwitterClass

class CuriosidadesClass:
    """
    Classe de curiosidades
    """
    def __init__(self):
        
        # path json curiosidades
        path_curiosidades = "curiosidades.csv"
        
        # API do Twitter
        self.twitter_api = TwitterClass()
        
        # curiosidades
        self.lista_curiosidades = pd.read_csv("curiosidades.csv", sep=';', encoding='utf-8', header=None)[0]
        self.modulo = 'curiosidades'
        
        # mapeamento de meses
        self.dict_map_mes = {1: 'janeiro',
                             2: 'fevereiro',
                             3: 'março',
                             4: 'abril',
                             5: 'maio',
                             6: 'junho',
                             7: 'julho',
                             8: 'agosto',
                             9: 'setembro',
                             10: 'outubro',
                             11: 'novembro',
                             12: 'dezembro'
                             }

    
    def seleciona_curiosidade(self):
        '''
        Seleciona curiosidade da lista
        '''
        # tenta selecionar elemento aleatório da lista
        for tentativa in range(20):
            curiosidade = random.choice(self.lista_curiosidades)
            tweet = f"{self.twitter_api.get_inicio_post()}Você sabia?\n{curiosidade}\n\n{self.get_dia_atual()}{self.twitter_api.get_fim_post()}"
            flag_pode_ser_publicado = self.twitter_api.verifica_tweet_pode_ser_publicado(tweet)
            if flag_pode_ser_publicado == 1:
                return 1, tweet
            
        # não encontrou curiosidades novas
        print ('Não encontrei curiosidades novas')
        sys.exit(0)
    
    
    def get_dia_atual(self):
        '''
        data de hoje
        '''
        # data de hoje
        dia = date.today().strftime("%d")
        mes = self.dict_map_mes[int(date.today().strftime("%m"))]
        ano = date.today().strftime("%Y")
        return f"{dia} de {mes} de {ano}"
    
    
    def prepara_tweet(self):
        '''
        Prepara tweet
        '''
        flag_pode_ser_publicado, tweet = self.seleciona_curiosidade()
        if flag_pode_ser_publicado == 0:
            return 0, ""
        
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
            sys.exit(0)

        # tenta publicar 
        try:
            self.twitter_api.make_tweet(tweet, self.modulo, "vazio", "vazio")
            print ('Tweet publicado!')

        # algo deu errado
        except Exception as e:
            print (f'Erro! {e}')