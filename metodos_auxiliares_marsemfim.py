import pandas as pd
import numpy as np
import requests
import random
import heapq
import nltk
import time
import json
import sys
import re
from datetime import date
from bs4 import BeautifulSoup
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
        self.chromeOptions.add_argument('headless')
        self.chromeOptions.add_argument(f"User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582")

        # parâmetros
        self.url = "https://marsemfim.com.br"
        self.max_publicacoes = 3
        self.flag_resumo = 1
        self.modulo = 'marsemfim'
    
    
    def prepara_tweet(self, noticia, link, flag):
        '''
        retorna tweet tratado
        '''
        if flag == 0:
            return f"{self.twitter_api.get_inicio_post()}{noticia}\n\nFonte: {link}{self.twitter_api.get_fim_post()}"
        else:
            return f"{self.twitter_api.get_inicio_post()}{noticia}\n\nFonte: {link}{self.twitter_api.get_fim_post()}\n\nResumo da publicação abaixo! {self.twitter_api.dict_map_emoji['dedo_baixo']}"
        

    def pesquisa_noticias(self):
        '''
        publica conteudo
        '''
         
        try:
            lista_news = []
        
            # entra na url
            driver = webdriver.Chrome(self.path_to_chromedriver, options=self.chromeOptions)
            driver.get(self.url)

            elemento_pesquisa = '//h3[contains(@class, "entry-title td-module-title")]/a'
            lista_elementos = driver.find_elements_by_xpath(elemento_pesquisa)
            max_elementos = max(len(lista_elementos), 10)
            lista_elementos = lista_elementos[:max_elementos]
        except:
            sys.exit(0)
                
        for elemento in lista_elementos:
            try:
                texto = elemento.text
                link = elemento.get_attribute("href")
                
                # gera resumo da notícia
                try:
                    soup = BeautifulSoup(requests.get(link).content)
                    resumo_pt1 = soup.find("h2", {"style": "text-align: justify;"}).text
                    resumo_pt2 = soup.find("p", {"style": "text-align: justify;"}).text
                    resumo = f"{resumo_pt1}. {resumo_pt2}"
                except:
                    resumo = ''

                # coloca noticia e link na lista
                lista_news.append([texto, link, resumo])
            except:
                continue

        # sorteia ordem de publicação
        try:
            random.shuffle(lista_news)
            driver.close()
            return lista_news
        except:
            sys.exit(0)
    
    
    def prepara_lista_resumos(self, resumo):
        '''
        retorna lista de textos de resumo
        '''
        regex_pattern = r"[,.?!]"
        frases = [frase for frase in re.split(r'(?<=[\,\.\!\?])\s*', resumo) if len(frase) >= 10]

        combined = []
        while frases:
            items = next((frases[:n] for n in range(len(frases),0,-1) if len(" ".join(frases[:n]))<=270), frases[:1])
            combined.append(" ".join(items))
            frases = frases[len(items):]

        return combined
        
        
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

        try:
            if (len(lista_news) == 0):
                return
        except:
            return
        
        # itera lista de noticias
        contador_publicacoes = 0
        for elemento in lista_news:
            
            # máximo número de publicações
            if (contador_publicacoes >= self.max_publicacoes):
                break

            try:
                # cria o tweet
                noticia = elemento[0]
                link = elemento[1]
                resumo = elemento[2]
                
                # tweet com e sem continuação
                tweet_0 = self.prepara_tweet(noticia, link, 0)
                tweet_1 = self.prepara_tweet(noticia, link, 1)
                
                # prepara resumo
                lista_resumos = self.prepara_lista_resumos(resumo)
                len_lista_resumos = len(lista_resumos)

                # valida se tweet está ok
                if self.twitter_api.verifica_tweet_pode_ser_publicado(tweet_0) and self.twitter_api.valida_tamanho_tweet(tweet_0):
                    
                    if (self.flag_resumo == 0 or len(resumo) <= 10 or len_lista_resumos == 0):
                        self.twitter_api.make_tweet(tweet_0, self.modulo)
                        print ('Tweet publicado!')
                        contador_publicacoes+=1
                        continue
                        
                    else:
                        # valida resumos
                        for resumo in lista_resumos:
                            if not (self.twitter_api.verifica_tweet_pode_ser_publicado(resumo)):
                                self.twitter_api.make_tweet(tweet_0, self.modulo)
                                print ('Tweet publicado!')
                                contador_publicacoes+=1
                                continue
                         
                        # publica tweet e depois resumos
                        try:
                            status = self.twitter_api.make_tweet(tweet_1, self.modulo)
                            status_id = str(status.id_str)
                        except:
                            continue
                        
                        # itera na lista de resumos
                        for indice_resumo in range(len_lista_resumos):
                            resumo = lista_resumos[indice_resumo]
                            
                            # coloca emoji do robô
                            resumo = f"{self.twitter_api.dict_map_emoji['robo']} {resumo}"
                            
                            # se possui mais texto para publicar no resumo
                            if (indice_resumo < (len_lista_resumos - 1)):
                                resumo = f"{resumo} {self.twitter_api.dict_map_emoji['tres_pontos']}"
                            
                            # publica tweet do resumo
                            status = self.twitter_api.make_tweet(resumo, self.modulo, tweet_id=str(status.id_str))
                    
                        print ('Tweet publicado!')
                        time.sleep(60)
                        contador_publicacoes+=1

            # erro
            except Exception as e:
                print (f'Erro! {e}')