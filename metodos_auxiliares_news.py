import pandas as pd
import numpy as np
import requests
import sys
import urllib
import json
from datetime import date
from bs4 import BeautifulSoup
from twitter_api import Twitter_Class


class HelperClassNews:
    """
    Classe de métodos auxiliares
    """
    def __init__(self):
        
        # arquivos auxiliares
        path_json_parametros_news="parametros_news.json"
        path_json_parametros_twitter="parametros_twitter.json"
        self.path_noticias_bd="noticias_bd.csv"

        # leitura do arquivo json com os parâmetros das notícias
        f = open(path_json_parametros_news, "r")
        infos = json.load(f)
        self.dict_header = {"User-Agent":infos['header']}
        self.url_google_news = infos['url_google_news']
        self.lista_pesquisas = infos['lista_pesquisas']
        self.max_news_check = int(infos['max_news_check'])
        self.url_tinyurl = infos['url_tinyurl']
        f.close()
        
        # leitura do arquivo json com os parâmetros
        f = open(path_json_parametros_twitter, "r")
        infos = json.load(f)
        self.limite_caracteres = int(infos['limite_caracteres'])
        self.flag_tweet = int(infos["flag_tweet"])
        f.close()

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
        return f"{noticia}\nLink: {link}\n\n{data}\n#redebotsdobem"

    
    # seleciona melhor notícia para tweetar
    def seleciona_tweet_noticias(self, df_news):
        '''
        selecionador de melhor notícia
        '''
        # csv de noticias
        lista_news_publicadas = pd.read_csv(self.path_noticias_bd, sep=';')['Noticia'].values.tolist()

        # filtra noticias que ainda não foram publicadas
        df_news = df_news.loc[~df_news['Noticia'].isin(lista_news_publicadas)]
        
        if (len(df_news) == 0):
            print ('df vazio')
            return 0, "", "" 

        # primeira linha das notícias
        try:
            df_tweet = df_news.sample(1).iloc[0]
        except:
            return 0, "", ""

        # data de hoje
        data_hoje = self.get_dia_atual()

        # cria o tweet
        tweet = self.prepara_tweet(df_tweet['Noticia'], df_tweet['Link'], data_hoje)

        # verifica se tweet está ok
        if (Twitter_Class.verifica_tweet_ok(tweet) and len(tweet) <= self.limite_caracteres):
            return 1, df_tweet['Noticia'], tweet
        else:
            return 0, "", ""
    
    def adiciona_noticia_bd(self, noticia):
        '''
        adiciona notícia ao bd
        '''
        df_noticias = pd.read_csv(self.path_noticias_bd, sep=';')
        df_noticias.loc[-1] = [noticia, date.today().strftime("%d/%m/%Y")]
        df_noticias.index = df_noticias.index + 1
        df_noticias = df_noticias.sort_index().iloc[:10_000]
        df_noticias.to_csv(self.path_noticias_bd, index=False, sep=';')

        
    def posta_tweet_noticia(self, df_news):
        '''
        verifica se tweet está ok e publica no Twitter
        '''
        flag_tweet_ok, noticia, tweet = self.seleciona_tweet_noticias(df_news)
        
        if (self.flag_tweet != 1):
            print ("Flag 1. Não posso publicar!")
            return

        # verifica se tweet está ok
        if (flag_tweet_ok):
            try:
                twitter_api = Twitter_Class()
                self.adiciona_noticia_bd(noticia)
                twitter_api.make_tweet(tweet)
                print ('Tweet publicado!')
            except Exception as e:
                print ('Não consegui publicar.')
                print (f"Erro: {e}")

        else:
            print ('Não consegui publicar. Algo errado no tweet.')

                
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

                # tenta gerar tinyurl
                try:
                    status, url_short = self.gera_url_tinyurl(url_long)
                    if (status != 1):
                        continue 
                except Exception as e:
                    continue

                # coloca noticia e link na lista
                lista_news.append([noticia, url_short])

        return pd.DataFrame(lista_news, columns=['Noticia', 'Link'])