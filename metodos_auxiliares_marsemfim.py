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
        
        # arquivos auxiliares
        path_json_parametros="parametros_marsemfim.json"
        
         # path do chromedriver
        self.path_to_chromedriver = 'chromedriver'
        
        # API do Twitter
        self.twitter_api = TwitterClass()
        
        # parametros do webdriver
        self.chromeOptions = webdriver.ChromeOptions()
        self.chromeOptions.add_argument('--no-sandbox')
        self.chromeOptions.add_argument("--headless")

        # leitura do arquivo json com os parâmetros das notícias
        f = open(path_json_parametros, "r")
        infos = json.load(f)
        self.dict_header = {"User-Agent":infos['header']}
        self.url = infos['url']
        self.url_tinyurl = infos['url_tinyurl']
        f.close()

        # mapeamento de meses
        self.dict_map_mes = self.twitter_api.get_map_meses()
        
        # hashtag do post
        self.hashtag = f"\n#AmazôniaAzul {self.twitter_api.dict_map_emoji['oceano']}"\
        +f"\n#redebotsdobem {self.twitter_api.dict_map_emoji['satelite']}"


    # retorna dia atual
    def get_dia_atual(self):
        '''
        retorna dia atual em portugês
        '''
        # data de hoje
        dia = date.today().strftime("%d")
        mes = self.dict_map_mes[int(date.today().strftime("%m"))]
        ano = date.today().strftime("%Y")
        return f"{dia} de {mes} de {ano}"
    
    
    def prepara_tweet(self, noticia, link, data):
        '''
        retorna tweet tratado
        '''
        return f"{self.twitter_api.dict_map_emoji['robo']} {noticia}\n\nFonte: {link}\n\n{data}" + self.hashtag

                
    def gera_url_tinyurl(self, url_long):
        '''
        Transforma URL longa em URL curta (tinyurl)
        '''
        try:
            url = self.url_tinyurl + "?" + urllib.parse.urlencode({"url": url_long})
            res = requests.get(url)
            return 1, res.text
        except Exception as e:
            return 0, ''
        
      
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
            
            # tenta gerar tinyurl
            try:
                status, url_short = self.gera_url_tinyurl(link)
                if (status != 1):
                    continue
            except Exception as e:
                continue

            # coloca noticia e link na lista
            lista_news.append([texto, url_short])

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
        
        # data de hoje
        data_hoje = self.get_dia_atual()
        
        for elemento in lista_news:

            try:
                # cria o tweet
                noticia = elemento[0]
                link = elemento[1]
                tweet = self.prepara_tweet(noticia, link, data_hoje)

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