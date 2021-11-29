import pandas as pd
import numpy as np
import requests
import sys
import urllib
import json
from datetime import date
from bs4 import BeautifulSoup
from twitter_api import TwitterClass


class HelperClassNews:
    """
    Classe de métodos auxiliares
    """
    def __init__(self):
        
        # arquivos auxiliares
        path_json_parametros_news="parametros_news.json"
        
        # API do Twitter
        self.twitter_api = TwitterClass()

        # leitura do arquivo json com os parâmetros das notícias
        f = open(path_json_parametros_news, "r")
        infos = json.load(f)
        self.dict_header = {"User-Agent":infos['header']}
        self.url_google_news = infos['url_google_news']
        self.lista_pesquisas = infos['lista_pesquisas']
        self.max_news_check = int(infos['max_news_check'])
        self.url_tinyurl = infos['url_tinyurl']
        f.close()

        # mapeamento de meses
        self.dict_map_mes = self.twitter_api.get_map_meses()
        
        # hashtag do post
        self.hashtag = "\n#AmazôniaAzul\n#redebotsdobem"


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
        return f"{noticia}\n\nLink: {link}\n\n{data}" + self.hashtag

    
    # seleciona melhor notícia para tweetar
    def seleciona_tweet_noticias(self, df_news):
        '''
        selecionador de melhor notícia
        '''
          
        if (len(df_news) == 0):
            return 0, "", ""
        
        # data de hoje
        data_hoje = self.get_dia_atual()
        
        try:
            for index in range(len(df_news['Noticia'])):

                # cria o tweet
                noticia = df_news.iloc[index]['Noticia']
                link = df_news.iloc[index]['Link']
                tweet = self.prepara_tweet(noticia, link, data_hoje)
                
                # verifica se tweet está ok
                if (self.twitter_api.verifica_tweet_pode_ser_publicado(tweet) and self.twitter_api.valida_tamanho_tweet(tweet)):
                    return 1, df_news['Noticia'], tweet
                
        except:
             return 0, "", ""
        
        # se nada deu certo..
        return 0, "", ""

        
    def posta_tweet_noticia(self):
        '''
        verifica se tweet está ok e publica no Twitter
        '''
        
        # flag de publicação
        if (self.twitter_api.get_status_twitter() != 1):
            print ("Flag 0. Não posso publicar!")
            return
        
        # pesquisa notícias
        df_news = self.pesquisa_news()

        # seleciona noticia
        flag_tweet_ok, noticia, tweet = self.seleciona_tweet_noticias(df_news)

        # verifica se tweet está ok
        if (flag_tweet_ok):
            try:
                self.twitter_api.make_tweet(tweet)
                print ('Tweet publicado!')
            except Exception as e:
                print ('Não consegui publicar.')
                print (f"Erro: {e}")

        else:
            print ('Não consegui publicar. Algo está errado.')

                
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