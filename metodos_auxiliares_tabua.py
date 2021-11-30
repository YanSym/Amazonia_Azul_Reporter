import pandas as pd
import numpy as np
import requests
import random
import urllib
import json
import time
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from twitter_api import TwitterClass


class HelperClassTabua:
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
        self.tempo_espera_tweet_segundos = int(infos['tempo_espera_tweet_segundos'])
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

        self.lista_colunas_init = ['Cidade', 'UF', 'Dia', '1_Mare', '2_Mare', '3_Mare', '4_Mare']
        
        # colunas de mares
        self.lista_colunas_finais = ['Cidade',
                                     'UF',
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
                                 'UF',
                                 'Tempo',
                                 'Temperatura',
                                 'Temperatura_Max',
                                 'Temperatura_Min',
                                 'Sensacao_Termica',
                                 'Nebulosidade',
                                 'Umidade',
                                 'Vento',
                                 'Pesca',
                                 'Ultra_Violeta',
                                 'Tempo_Prox_Evento',
                                 'Proximo_Evento']
        
        
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
        self.path_tempo_proximo_evento = '//*[@id="grafico_estados_luna"]/div[1]/div[5]/strong'
        self.path_proximo_evento = '//*[@id="grafico_estados_luna"]/div[1]/div[6]/strong/em'
        
        # mapeamento de meses
        self.dict_map_mes = self.twitter_api.get_map_meses()
        
        # data de hoje
        dia = date.today().strftime("%d")
        mes = self.dict_map_mes[int(date.today().strftime("%m"))]
        ano = date.today().strftime("%Y")
        self.data_hoje_completa = f"{dia} de {mes} de {ano}"

        # hashtag do post
        self.hashtag = "\n#AmazôniaAzul\n#redebotsdobem"
    
    
    # trata elemento removendo caracteres incorretos
    def trata_elemento(self, element):
        '''
        Trata elemento, removendo caracteres indesejados
        '''
        return element.text.replace('\n','')\
                            .replace('\t','')\
                            .replace('\r','')\
                            .replace('m', '')\
                            .strip()
    
    
    def gera_resultados_mares_dia(self):
        '''
        Gera resultados de marés do dia
        '''
        
        dia_hoje = int(date.today().strftime("%d"))
        
        lista_dfs = []
        lista_dados = []

        # itera cidades
        for index, row in self.df_cidades.iterrows():

            try:

                cidade = row['Cidade']
                uf = row['UF']
                valor = row['Tabua_mares']

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
                            lista_dados.append([cidade, uf] + [ele for ele in cols if ele])
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
        '''
        Gera resultados dos climas
        '''
    
        lista_infos = []

        # itera cidades
        for index, row in self.df_cidades.iterrows():

            try:

                cidade = row['Cidade']
                uf = row['UF']
                valor = row['Tabua_mares']

                # cria urls
                url_dia = f"{self.url_tabua_mares}/{valor}"

                # entra na url
                driver = webdriver.Chrome(self.path_to_chromedriver, options=self.chromeOptions)
                driver.get(url_dia)

                # leitura do conteúdo
                tempo = driver.find_element_by_xpath(self.path_tempo).text
                temperatura = int(driver.find_element_by_xpath(self.path_temperatura).text)
                temperatura_max = int(driver.find_element_by_xpath(self.path_temperatura_max).text)
                temperatura_min = int(driver.find_element_by_xpath(self.path_temperatura_min).text)
                sensacao = int(driver.find_element_by_xpath(self.path_sensacao_termica).text)
                nebulosidade = int(driver.find_element_by_xpath(self.path_nebulosidade).text)
                umidade = int(driver.find_element_by_xpath(self.path_umidade).text)
                vento = int(driver.find_element_by_xpath(self.path_vento).text)
                ultra_violeta = int(driver.find_element_by_xpath(self.path_ultra_violeta).text)         
                tempo_proximo_evento = driver.find_element_by_xpath(self.path_tempo_proximo_evento).text
                proximo_evento = driver.find_element_by_xpath(self.path_proximo_evento).text
                    
                # trata tempo
                tempo = tempo.replace('Nublado', 'Céu nublado').lower()

                # pesca
                pesca_muito_bom = driver.find_element_by_xpath(self.path_pesca_muito_bom).get_attribute("class")
                pesca_bom = driver.find_element_by_xpath(self.path_pesca_bom).get_attribute("class")
                pesca_mau = driver.find_element_by_xpath(self.path_pesca_mau).get_attribute("class")

                # trata pesca
                if pesca_muito_bom == 'circulo_estado_grafico_barometro1 circulo_estado_grafico_barometro1_activo':
                    pesca = 'Muito Bom'
                elif pesca_bom == 'circulo_estado_grafico_barometro1 circulo_estado_grafico_barometro1_activo':
                    pesca = 'Bom'
                elif pesca_mau == 'circulo_estado_grafico_barometro1 circulo_estado_grafico_barometro1_activo':
                    pesca = 'Mau'
                else:
                    pesca = ''

                # salva lista
                lista_infos.append([cidade, uf, tempo,
                                    temperatura, temperatura_max, temperatura_min,
                                    sensacao, nebulosidade, umidade, vento,
                                    pesca, ultra_violeta,
                                    tempo_proximo_evento, proximo_evento])

            except Exception as e:
                continue

        # fecha o driver
        driver.close()

        # cria o dataframe
        df_infos = pd.DataFrame(lista_infos,
                                columns=self.lista_colunas_df)
        
        # retorna resultados
        return df_infos
    
    
    def gera_df_tabua_mares(self):
        '''
        Junta resultados e aplica pós-processamentos para garantir coerência dos dados
        '''
        df_tabua_mares = self.gera_resultados_mares_dia()
        df_clima = self.gera_resultados_climas()
        
        # junta resultados
        df_resultado = pd.merge(df_tabua_mares,
                                df_clima,
                                on=['Cidade', 'UF'],
                                how='inner')
        
        # checks de sanidade
        df_resultado['Temperatura_Max'] = df_resultado[["Temperatura", "Temperatura_Max", "Temperatura_Min"]].max(axis=1)
        df_resultado['Temperatura_Min'] = df_resultado[["Temperatura", "Temperatura_Max", "Temperatura_Min"]].min(axis=1)
        
        # retorna resultados
        return df_resultado
    
    
    def seleciona_conteudo_publicar(self, df_resultados):
        '''
        Seleciona conteúdo para publicar, de acordo com a estratégia implementada
        '''

        # estratéga de seleção de conteúdo
        df_selecionados = df_resultados.sample(5)
        
        # retorna resultados selecionados
        return df_selecionados
    
    
    def mapeia_conteudo_estado(self, df_linha):
        '''
        Mapeia conteúdo em um estado
        '''
        ultra_violeta = df_linha['Ultra_Violeta']
        
        # índice ultra violeta máximo
        if ultra_violeta == 11:
            return 1
        
        # índice ultra violeta
        else:
            return 2
    
    
    def atribui_template(self, df_linha, estado):
        '''
        Retorna template
        '''
        
        # campos
        cidade = df_linha['Cidade']
        uf = df_linha['UF']
        tempo = df_linha['Tempo']
        temperatura = df_linha['Temperatura']
        sensacao_termica = df_linha['Sensacao_Termica']
        temperatura_max = df_linha['Temperatura_Max']
        temperatura_min = df_linha['Temperatura_Min']
        nebulosidade = df_linha['Nebulosidade']
        ultra_violeta = df_linha['Ultra_Violeta']
        vento = df_linha['Vento']

        # Ultra Violeta
        if estado == 1:

            possibilidade_1 = f'''
            Em {cidade} ({uf}) a previsão do tempo é de {tempo}, com uma temperatura de {temperatura}°C e sensação térmica de {sensacao_termica}°C.\nA temperatura máxima prevista é de {temperatura_max}°C e a mínima de {temperatura_min}°C.
            '''
            
            possibilidade_2 = f'''
            Em {cidade} ({uf}) a previsão do tempo é de {tempo}, com uma temperatura de {temperatura}°C e sensação térmica de {sensacao_termica}°C.\nO índice ultravioleta ({ultra_violeta}) hoje está elevado ({ultra_violeta}). Utilize protetor solar, camiseta e óculos de sol!
            '''
            
            possibilidade_3 = f'''
            Em {cidade} ({uf}) a previsão do tempo é de {tempo}, com uma temperatura de {temperatura}°C e sensação térmica de {sensacao_termica}°C.\nO índice ultravioleta ({ultra_violeta}) hoje está elevado ({ultra_violeta}). Fique à sombra durante as horas centrais do dia!
            '''
            
            lista_possibilidades = [possibilidade_1, possibilidade_2, possibilidade_3]
            tweet = random.choice(lista_possibilidades)
        
        
        # Não Ultra Violeta  
        elif estado == 2:
            
            possibilidade_1 = f'''
            Em {cidade} ({uf}) a previsão do tempo é de {tempo}, com uma temperatura de {temperatura}°C e sensação térmica de {sensacao_termica}°C.\nA temperatura máxima prevista é de {temperatura_max}°C e a mínima de {temperatura_min}°C.
            '''
            
            possibilidade_2 = f'''
            Em {cidade} ({uf}) a previsão do tempo é de {tempo}, com uma temperatura de {temperatura}°C e sensação térmica de {sensacao_termica}°C.\nA nebulosidade é de {nebulosidade}% e a velocidade do vento é de {vento} km/h.
            '''
            
            lista_possibilidades = [possibilidade_1, possibilidade_2]
            tweet = random.choice(lista_possibilidades)
            
        else:
            return 0, ""
        
        # adiciona pós-processamento
        tweet = (tweet + "\n\n" + self.data_hoje_completa + self.hashtag)
        
        return 1, tweet
    
    
    def publica_conteudo(self):
        '''
        Publica previsão do tempo (tábua de marés)
        '''
        
        # flag de publicação
        if (self.twitter_api.get_status_twitter() != 1):
            print ("Flag 0. Não posso publicar!")
            return
        
        try:
            # gera resultados
            df_resultados = self.gera_df_tabua_mares()

            # filtra dados para publicação
            df_selecionados = self.seleciona_conteudo_publicar(df_resultados)
        
        except:
            return
        
        if (len(df_selecionados) == 0):
            return  
        
        # tenta publicar tweets
        try:
            for index in range(len(df_selecionados)):
                
                df_linha = df_selecionados.iloc[index]

                # estado (contexto) do conjunto de dados
                estado = self.mapeia_conteudo_estado(df_linha)
                
                # cria o tweet
                flag, tweet = self.atribui_template(df_linha, estado)
                
                # verifica se pode publicar o tweet
                if (flag == 0):
                    print ('tweet não pode ser publicado')
                    continue
                    
                
                # verifica se tweet está ok
                if (self.twitter_api.verifica_tweet_pode_ser_publicado(tweet) and self.twitter_api.valida_tamanho_tweet(tweet)):
                    try:
                        self.twitter_api.make_tweet(tweet)
                        print ('Tweet publicado')
                        
                        # espera um tempo para publicar novamente
                        time.sleep(self.tempo_espera_tweet_segundos)
                        
                    except Exception as e:
                        print ('Não consegui publicar.')
                        print (f"Erro: {e}")
                        
                else:
                    print ('tweet não pode ser publicado')
                
        except:
             return