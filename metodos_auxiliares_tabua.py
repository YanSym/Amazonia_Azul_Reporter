import pandas as pd
import numpy as np
import requests
import urllib
import json
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from twitter_api import Twitter_Class


class HelperClassTabua:
    """
    Classe de métodos auxiliares
    """
    def __init__(self):
        
        # path do chromedriver
        self.path_to_chromedriver = 'chromedriver'
        
        # parametros do webdriver
        self.chromeOptions = webdriver.ChromeOptions()
        self.chromeOptions.add_argument('--no-sandbox')
        self.chromeOptions.add_argument("--headless")
        
        # arquivos auxiliares
        self.path_json_parametros_tabua="parametros_tabua_mares.json"
        self.path_json_parametros_twitter="parametros_twitter.json"
        self.path_palavras_banidas="lista_palavras_banidas.txt"
        self.path_infos_cidades='infos_cidades.csv'
        
        # leitura do arquivo json com os parâmetros das notícias
        f = open(self.path_json_parametros_tabua, "r")
        infos = json.load(f)
        self.dict_header = {"User-Agent":infos['header']}
        self.url_tabua_mares = infos['url_tabua_mares']
        f.close()
        
        # leitura do arquivo json com os parâmetros
        f = open(self.path_json_parametros_twitter, "r")
        infos = json.load(f)
        self.limite_caracteres = int(infos['limite_caracteres'])
        self.flag_tweet = int(infos["flag_tweet"])
        f.close()

        # Leitura das palavras banidas
        f = open(self.path_palavras_banidas, "r")
        self.lista_palavras_banidas = f.read().split('\n')
        f.close()
        
        # df cidades
        self.df_cidades = pd.read_csv(self.path_infos_cidades, encoding='latin-1', sep=';')

        self.lista_colunas_init = ['Cidade', 'Estado', 'Dia', '1_Mare', '2_Mare', '3_Mare', '4_Mare']
        
        # colunas de mares
        self.lista_colunas_finais = ['Cidade',
                        'Estado',
                        '1_Mare_Horario',
                        '1_Mare_Altura',
                        '2_Mare_Horario',
                        '2_Mare_Altura',
                        '3_Mare_Horario',
                        '3_Mare_Altura',
                        '4_Mare_Horario',
                        '4_Mare_Altura']
        
        
        # colunas de clima
        self.lista_colunas_df = ['Cidade',
                            'Estado',
                            'Tempo',
                            'Temperatura',
                            'Temperatura_Max',
                            'Temperatura_Min',
                            'Sensacao_Termica',
                            'Nebulosidade',
                            'Umidade',
                            'Vento',
                            'Pesca',
                            'Ultra_Violeta']
        
        
        # paths atual
        self.path_tempo = '//*[@id="estado_tiempo_actual_txt"]'
        self.path_temperatura = '//*[@id="temperatura_grafico_termometro"]'
        self.path_temperatura_max = '//*[@id="temperatura_grafico_termometro_max"]'
        self.path_temperatura_min = '//*[@id="temperatura_grafico_termometro_min"]'
        self.path_nebulosidade = '//*[@id="nubosidad_actual_txt_span"]'
        self.path_umidade = '//*[@id="humedad_grafico_humedad"]'
        self.path_vento ='//*[@id="numeros_datos_grafico_tiempo_brujula"]/span[1]'
        self.path_sensacao_termica = '//*[@id="temperatura_grafico_termometro_sensacion"]'
        self.path_pesca_muito_bom = '//*[@id="circulo_estado_grafico_barometro1_1"]'
        self.path_pesca_bom = '//*[@id="circulo_estado_grafico_barometro2_1"]'
        self.path_pesca_mau = '//*[@id="circulo_estado_grafico_barometro3_1"]'
        self.path_ultra_violeta = '//*[@id="uv_maximo_img_num"]'
        

    # retorna dia atual
    def get_dia_atual(self):
        # data de hoje
        dia = date.today().strftime("%d")
        mes = self.dict_map_mes[int(date.today().strftime("%m"))]
        ano = date.today().strftime("%Y")
        return f"{dia} de {mes} de {ano}"
    
    
    # trata elemento removendo caracteres incorretos
    def trata_elemento(self, element):
        return element.text.replace('\n','')\
                            .replace('\t','')\
                            .replace('\r','')\
                            .replace('m', '')\
                            .strip()
    
    
    def gera_resultados_mares_dia(self):
        
        dia_hoje = int(date.today().strftime("%d"))
        
        lista_dfs = []
        lista_dados = []

        # itera cidades
        for index, row in self.df_cidades.iterrows():

            try:

                cidade = row['cidade']
                estado = row['estado']
                valor = row['tabua_mares']

                # cria urls
                url_cidade = f"{self.url_tabua_mares}/{valor}"

                # leitura das informações da cidade
                html_text = requests.get(url_cidade, headers=self.dict_header).text
                soup = BeautifulSoup(html_text, 'html.parser')
                table = soup.find('table', attrs={'id':'tabla_mareas_swipe1'})

                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    cols = [self.trata_elemento(ele) for ele in cols if ele]

                    # insere somente dia de hoje
                    try:
                        if int(cols[0].split(' ')[0]) == dia_hoje:
                            lista_dados.append([cidade, estado] + [ele for ele in cols if ele])
                    except:
                        continue

            except Exception as e:
                print (f'erro: {e} | cidade: {cidade}')

        df = pd.DataFrame(lista_dados, columns=self.lista_colunas_init)

        # split
        df[['1_Mare_Horario', '1_Mare_Altura']] = df['1_Mare'].str.split(' ', 1, expand=True)
        df[['2_Mare_Horario', '2_Mare_Altura']] = df['2_Mare'].str.split(' ', 1, expand=True)
        df[['3_Mare_Horario', '3_Mare_Altura']] = df['3_Mare'].str.split(' ', 1, expand=True)
        df[['4_Mare_Horario', '4_Mare_Altura']] = df['4_Mare'].str.split(' ', 1, expand=True)

        df = df.drop(columns=['Dia', '1_Mare', '2_Mare', '3_Mare', '4_Mare'], axis=1)
        df = df[self.lista_colunas_finais].fillna('')
        return df
    
    
    def gera_resultados_climas(self):
    
        lista_infos = []

        # itera cidades
        for index, row in self.df_cidades.iterrows():

            try:

                cidade = row['cidade']
                estado = row['estado']
                valor = row['tabua_mares']

                # cria urls
                url_dia = f"{self.url_tabua_mares}/{valor}"

                # entra na url
                driver = webdriver.Chrome(self.path_to_chromedriver, options=self.chromeOptions)
                driver.get(url_dia)

                # leitura do conteúdo
                tempo = driver.find_element_by_xpath(self.path_tempo).text
                temperatura = driver.find_element_by_xpath(self.path_temperatura).text
                temperatura_max = driver.find_element_by_xpath(self.path_temperatura_max).text
                temperatura_min = driver.find_element_by_xpath(self.path_temperatura_min).text
                sensacao = driver.find_element_by_xpath(self.path_sensacao_termica).text
                nebulosidade = driver.find_element_by_xpath(self.path_nebulosidade).text
                umidade = driver.find_element_by_xpath(self.path_umidade).text
                vento = driver.find_element_by_xpath(self.path_vento).text
                ultra_violeta = driver.find_element_by_xpath(self.path_ultra_violeta).text

                # pesca
                pesca_muito_bom = driver.find_element_by_xpath(self.path_pesca_muito_bom).get_attribute("class")
                pesca_bom = driver.find_element_by_xpath(self.path_pesca_bom).get_attribute("class")
                pesca_mau = driver.find_element_by_xpath(self.path_pesca_mau).get_attribute("class")

                # trata pesca
                if pesca_muito_bom == 'circulo_estado_grafico_barometro1 circulo_estado_grafico_barometro1_activo':
                    pesca = 'Muito Bom'
                elif pesca_bom == 'circulo_estado_grafico_barometro2 circulo_estado_grafico_barometro2_activo':
                    pesca = 'Bom'
                elif pesca_mau == 'circulo_estado_grafico_barometro2 circulo_estado_grafico_barometro3_activo':
                    pesca = 'Mau'
                else:
                    pesca = ''

                # salva lista
                lista_infos.append([cidade, estado, tempo,
                                    temperatura, temperatura_max, temperatura_min,
                                    sensacao, nebulosidade, umidade, vento,
                                    pesca, ultra_violeta])

            except Exception as e:
                print (f'erro: {e}')

        # fecha o driver
        driver.close()

        # cria o dataframe
        df_infos = pd.DataFrame(lista_infos,
                                columns=self.lista_colunas_df)
        
        # retorna resultados
        return df_infos
    
    
    def gera_df_tabua_mares(self):
        df_tabua_mares = self.gera_resultados_mares_dia()
        df_clima = self.gera_resultados_climas()
        
        # junta resultados
        df_resultado = pd.merge(df_tabua_mares,
                                df_clima,
                                on=['Cidade', 'Estado'],
                                how='inner')
        return df_resultado
    
    
