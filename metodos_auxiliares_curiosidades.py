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
        self.dict_map_mes = self.twitter_api.get_map_meses()
        
        # data de hoje
        dia = date.today().strftime("%d")
        mes = self.dict_map_mes[int(date.today().strftime("%m"))]
        ano = date.today().strftime("%Y")
        self.data_hoje_completa = f"{dia} de {mes} de {ano}"
        
        # hashtag do post
        self.hashtag = "\n#AmazôniaAzul\n#redebotsdobem"
        
        
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
            return 0, ""
        
        tweet = "Você sabia?\n" + curiosidade + "\n\n" + self.data_hoje_completa + self.hashtag
        
        # verifica se tamanho está ok
        if self.twitter_api.valida_tamanho_tweet(tweet) != 1:
            return 0, ""
        
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
        
        print (tweet)
        
        # tweet deu errado
        if flag == 0:
            return

        # tenta publicar 
        try:
            self.twitter_api.make_tweet(tweet)

        # algo deu errado
        except:
            print ('Não consegui publicar.')