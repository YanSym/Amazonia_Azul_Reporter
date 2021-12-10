import pandas as pd
import numpy as np
import requests
import sys
import urllib
import json
from datetime import date
from selenium import webdriver
from twitter_api import TwitterClass


class HelperClassMarsemfim:
    """
    Classe de métodos auxiliares
    """
    def __init__(self):
        
         # path do chromedriver
        self.path_to_chromedriver = 'chromedriver'
        
        # API do Twitter
        self.twitter_api = TwitterClass()
        
        # parametros do webdriver
        self.chromeOptions = webdriver.ChromeOptions()
        self.chromeOptions.add_argument('--no-sandbox')
        self.chromeOptions.add_argument("--headless")

        # parâmetros
        self.dict_header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"}
        self.url = "https://marsemfim.com.br"
    
    
    def prepara_tweet(self, noticia, link):
        '''
        retorna tweet tratado
        '''
        return f"{self.twitter_api.get_inicio_post()}{noticia}\n\nFonte: {link}{self.twitter_api.get_fim_post()}"
        
      
    def pesquisa_noticias(self):
        '''
        publica conteudo
        '''
         
        lista_news = []
        
        # entra na url
        driver = webdriver.Chrome(self.path_to_chromedriver, options=self.chromeOptions)
        driver.get(self.url)
        
        elemento_pesquisa = '//h3[contains(@class, "entry-title td-module-title")]/a'
        lista_elementos = driver.find_elements_by_xpath(elemento_pesquisa)[:3]
                
        for elemento in lista_elementos:
            texto = elemento.text
            link = elemento.get_attribute("href")

            # coloca noticia e link na lista
            lista_news.append([texto, link])

        return lista_news
    
    
    def publica_conteudo(self):
        '''
        verifica se tweet está ok e publica no Twitter
        '''
        
        # flag de publicação
        if (self.twitter_api.get_status_twitter() != 1):
            print ("Flag 0. Não posso publicar!")
            return
        
        # pesquisa notícias
        lista_news = self.pesquisa_noticias()

        if (len(lista_news) == 0):
            return
        
        # itera lista de noticias
        for elemento in lista_news:

            try:
                # cria o tweet
                noticia = elemento[0]
                link = elemento[1]
                
                
                tweet = self.prepara_tweet(noticia, link)

                # verifica se tweet está ok
                if (self.twitter_api.verifica_tweet_pode_ser_publicado(tweet) and self.twitter_api.valida_tamanho_tweet(tweet)):
                    self.twitter_api.make_tweet(tweet)
                    print ('Tweet publicado!')
                    return

            # erro
            except Exception as e:
                continue

        # não conseguiu publicar
        print ('Não consegui publicar. Algo está errado.')