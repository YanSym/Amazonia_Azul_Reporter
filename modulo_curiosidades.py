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

        # leitura do arquivo json com os parâmetros das notícias
        f = open(path_json_parametros_curiosidades, "r")
        infos = json.load(f)
        self.lista_dias = [int(dia) for dia in infos['lista_dias']]
        f.close()
        
        # dia de hoje
        self.dia_hoje = int(date.today().strftime("%d"))
        
        # curiosidades
        self.lista_curiosidades = pd.read_csv("curiosidades.csv", sep=';', encoding='latin1')['Curiosidade']
        
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
        
        # data de hoje
        dia = date.today().strftime("%d")
        mes = self.dict_map_mes[int(date.today().strftime("%m"))]
        ano = date.today().strftime("%Y")
        self.data_hoje_completa = f"{dia} de {mes} de {ano}"
        
        
    def check_dia_publicar(self):
        '''
        Verifica se é dia de publicar curiosidade
        '''
        if self.dia_hoje in self.lista_dias:
            return 1
        else:
            return 0
    
    
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
            return 1, ""
        
        tweet = "Você sabia?\n" + curiosidade + "\n\n" + self.data_hoje_completa + "\n#redebotsdobem"
        return 1, tweet
    
    
    def publica_curiosidade(self):
        '''
        Tenta publicar curiosidade
        '''
        
        # flag de publicação
        if (self.twitter_api.get_status_twitter() != 1):
            print ("Flag 0. Não posso publicar!")
            return
        
        # verifica se é dia de publicar curiosidade
        if not self.check_dia_publicar():
            return
        
        # seleciona curiosidade para publicar
        flag, tweet = self.prepara_tweet()
        
        # tweet deu errado
        if flag == 0:
            return

        # tenta publicar 
        try:
            self.twitter_api.make_tweet(tweet)

        # algo deu errado
        except:
            print ('Não consegui publicar. Algo está errado.')