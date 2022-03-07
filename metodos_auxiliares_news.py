import pandas as pd
import numpy as np
import requests
import urllib
import time
import json
import sys
import os
from datetime import date
from bs4 import BeautifulSoup
from twitter_api import TwitterClass


class HelperClassNews:
    """
    Classe de métodos auxiliares
    """
    def __init__(self):
        
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
        
        # dia atual
        print (self.get_dia_atual())
        
        # path atual
        self.current_path = str(os.getcwd())
        
        # arquivos auxiliares
        path_json_parametros_news = os.path.join(self.current_path, "parametros_news.json")
        
        # API do Twitter
        self.twitter_api = TwitterClass()
        
        # parâmetros globais
        self.dict_header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"}
        self.url_google_news = "https://news.google.com"
    
        # lista de pesquisas
        path_pesquisas = os.path.join(self.current_path, "pesquisas.csv")
        self.lista_pesquisas = pd.read_csv(path_pesquisas, sep=';', encoding='utf-8', header=None)[0]
        self.max_news_check = 5
        self.max_publicacoes = 3
        self.modulo = 'noticias'
        
        
    def get_dia_atual(self):
        '''
        data de hoje
        '''
        # data de hoje
        dia = date.today().strftime("%d")
        mes = self.dict_map_mes[int(date.today().strftime("%m"))]
        ano = date.today().strftime("%Y")
        return f"{dia} de {mes} de {ano}"
    
    
    def prepara_tweet(self, noticia, link):
        '''
        retorna tweet tratado
        '''
        
        return f"{self.twitter_api.get_inicio_post()}{noticia}\n\nFonte: {link}{self.twitter_api.get_fim_post()}"
    
    
    def gera_url_google_news(self, url):
        '''
        Gera url google news
        '''
        return (self.url_google_news + '/search?q=' + url.replace(" ", "+") + "&hl=pt-BR")
        
      
    def pesquisa_news(self):
        '''
        pesquisa notícias
        '''
         
        lista_news = []
                
        for pesquisa in self.lista_pesquisas:
            pesquisa = self.gera_url_google_news(pesquisa)
            response = requests.get(pesquisa, headers=self.dict_header)
            soup = BeautifulSoup(response.text, 'html.parser')

            for index, result in enumerate(soup.select('.xrnccd')):

                # interrompe execução
                if index >= self.max_news_check:
                    break

                # data da publicação
                data = result.find("time", {"class": "WW6dff uQIVzc Sksgp"}).text
                if ('hora' not in data.lower() and 'ontem' not in data.lower()):
                    continue
                    
                # noticia
                noticia = (result.h3.a.text)
                
                # link
                link = "https://news.google.com" + result.h3.a['href'][1:]
                url_long = requests.get(link).url

                # coloca noticia e link na lista
                lista_news.append([noticia, url_long])

        return pd.DataFrame(lista_news, columns=['Noticia', 'Link'])
    
    
         
    def publica_conteudo(self):
        '''
        verifica se tweet está ok e publica no Twitter
        '''
        
        # flag de publicação
        if (self.twitter_api.get_status_twitter() != 1):
            print ("Flag 0. Não posso publicar!")
            return
        
        # pesquisa notícias
        df_news = self.pesquisa_news()

        try:
            if (len(df_news) == 0):
                return
        except:
            return
        
        # itera lista de noticias
        contador_publicacoes = 0
        for index in range(len(df_news['Noticia'])):

            if (contador_publicacoes >= self.max_publicacoes):
                break
            
            try:
                # cria o tweet
                noticia = df_news.iloc[index]['Noticia']
                link = df_news.iloc[index]['Link']
                tweet = self.prepara_tweet(noticia, link)

                # verifica se tweet está ok
                if (self.twitter_api.verifica_tweet_pode_ser_publicado(tweet) and self.twitter_api.valida_tamanho_tweet(tweet)):
                    status = self.twitter_api.make_tweet(tweet, self.modulo, "vazio", "vazio")
                    if (status != 0):
                        print (tweet)
                        print ('Tweet publicado!')
                        contador_publicacoes+=1
                        time.sleep(60)

            # erro
            except Exception as e:
                continue