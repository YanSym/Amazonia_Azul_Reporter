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


class HelperClassTempo:
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
        self.path_infos_cidades='cidades.csv'
        
        # parâmetros
        self.dict_header = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"}
        self.url_tabua_mares = "https://tabuademares.com/br"
        self.tempo_espera_tweet_segundos = 10
        
        # df cidades
        self.df_cidades = pd.read_csv(self.path_infos_cidades, encoding='latin-1', sep=';')
        
        # colunas de clima
        self.lista_colunas_tempo = ['Cidade',
                                    'UF',
                                    'Tempo',
                                    'Temperatura',
                                    'Temperatura_Max',
                                    'Temperatura_Min',
                                    'Sensacao_Termica',
                                    'Nebulosidade',
                                    'Umidade',
                                    'Vento',
                                    'Ultra_Violeta',
                                    'Coeficiente_Mare',
                                    'Pesca',
                                    'Melhor_Horario_Pesca',
                                    '1_Mare_Horario',
                                    '1_Mare_Altura',
                                    '2_Mare_Horario',
                                    '2_Mare_Altura',
                                    '3_Mare_Horario',
                                    '3_Mare_Altura',
                                    '4_Mare_Horario',
                                    '4_Mare_Altura']
        
        
        # paths atual
        self.path_tempo = '//*[@id="estado_tiempo_actual_txt"]'
        self.path_temperatura = '//*[@id="temperatura_grafico_termometro"]'
        self.path_temperatura_max = '//*[@id="temperatura_grafico_termometro_max"]'
        self.path_temperatura_min = '//*[@id="temperatura_grafico_termometro_min"]'
        self.path_nebulosidade = '//*[@id="nubosidad_actual_txt_span"]'
        self.path_umidade = '//*[@id="humedad_grafico_humedad"]'
        self.path_vento ='//*[@id="numeros_datos_grafico_tiempo_brujula"]/span[1]'
        self.path_sensacao_termica = '//*[@id="temperatura_grafico_termometro_sensacion"]'
        self.path_ultra_violeta = '//*[@id="uv_maximo_img_num"]'
        self.path_coeficiente_mare = '//*[@id="noprint1"]/div[17]/div[2]/div[2]/div[1]/p/span[1]'
        self.path_peixe_1 = '//*[@id="salida_puesta_luna_actividad_peces"]/span[1]'
        self.path_peixe_2 = '//*[@id="salida_puesta_luna_actividad_peces"]/span[2]'
        self.path_peixe_3 = '//*[@id="salida_puesta_luna_actividad_peces"]/span[3]'
        self.path_horario_pesca1 = '//*[@id="salida_puesta_luna_periodos_fondo"]/div[1]/div[2]/div[1]/div[3]/div[3]/span[1]'
        self.path_horario_pesca2 = '//*[@id="salida_puesta_luna_periodos_fondo"]/div[1]/div[2]/div[1]/div[3]/div[3]/span[2]'
        self.path_horario_mare1 = '//*[@id="noprint1"]/div[17]/div[3]/div[2]/div[1]/div[5]/div[1]'
        self.path_altura_mare1 = '//*[@id="noprint1"]/div[17]/div[3]/div[2]/div[1]/div[5]/div[2]' 
        self.path_horario_mare2 = '//*[@id="noprint1"]/div[17]/div[3]/div[2]/div[1]/div[6]/div[1]'
        self.path_altura_mare2 = '//*[@id="noprint1"]/div[17]/div[3]/div[2]/div[1]/div[6]/div[2]'
        self.path_horario_mare3 = '//*[@id="noprint1"]/div[17]/div[3]/div[2]/div[1]/div[7]/div[1]'
        self.path_altura_mare3 = '//*[@id="noprint1"]/div[17]/div[3]/div[2]/div[1]/div[7]/div[2]'
        self.path_horario_mare4 = '//*[@id="noprint1"]/div[17]/div[3]/div[2]/div[1]/div[8]/div[1]'
        self.path_altura_mare4 = '//*[@id="noprint1"]/div[17]/div[3]/div[2]/div[1]/div[8]/div[2]'

    
    def get_inicio_texto(self, cidade):
        '''
        Retorna início do texto para publicação
        '''
        if cidade in ['Rio de Janeiro']:
            return 'no'
        else:
            return 'em'
    
    
    def gera_df_tabua_mares(self):
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
                coeficiente_mare = int(driver.find_element_by_xpath(self.path_coeficiente_mare).text)
                
                # condição de pesca no dia
                try:
                    peixe_1 = str(driver.find_element_by_xpath(self.path_peixe_1).get_attribute("class"))
                    peixe_2 = str(driver.find_element_by_xpath(self.path_peixe_2).get_attribute("class"))
                    peixe_3 = str(driver.find_element_by_xpath(self.path_peixe_3).get_attribute("class"))

                    # cria o campo de pesca
                    if peixe_3 == 'icon-ic_pez_gris':
                        pesca = 'Muito bom'
                    elif peixe_2 == 'icon-ic_pez_gris':
                        pesca = 'Bom'
                    elif peixe_1 == 'icon-ic_pez_gris':
                        pesca = 'Mediana'
                    else:
                        pesca = 'Ruim'
                except:
                    pesca = ''
                
                # cria o campo de melhor horário para pescar
                try:
                    horario_1 = str(driver.find_element_by_xpath(self.path_horario_pesca1).text)
                    horario_2 = str(driver.find_element_by_xpath(self.path_horario_pesca2).text)
                    melhor_horario_pesca = horario_1 + " - " + horario_2
                except:
                    melhor_horario_pesca = ""
                 
                # trata tempo
                tempo = tempo.replace('Nublado', 'Céu nublado').lower()
                
                
                # marés
                try:
                    mare_horario_1 = str(driver.find_element_by_xpath(self.path_horario_mare1).text).replace(" ", "").strip()
                    mare_altura_1 = str(driver.find_element_by_xpath(self.path_altura_mare1).text).replace(" ", "").strip()
                except:
                    mare_horario_1 = ""
                    mare_altura_1 = ""
                    
                try:
                    mare_horario_2 = str(driver.find_element_by_xpath(self.path_horario_mare2).text).replace(" ", "").strip()
                    mare_altura_2 = str(driver.find_element_by_xpath(self.path_altura_mare2).text).replace(" ", "").strip()
                except:
                    mare_horario_2 = ""
                    mare_altura_2 = ""
                    
                try: 
                    mare_horario_3 = str(driver.find_element_by_xpath(self.path_horario_mare3).text).replace(" ", "").strip()
                    mare_altura_3 = str(driver.find_element_by_xpath(self.path_altura_mare3).text).replace(" ", "").strip()
                except:
                    mare_horario_3 = ""
                    mare_altura_3 = ""
                
                try:
                    mare_horario_4 = str(driver.find_element_by_xpath(self.path_horario_mare4).text).replace(" ", "").strip()
                    mare_altura_4 = str(driver.find_element_by_xpath(self.path_altura_mare4).text).replace(" ", "").strip()
                except:
                    mare_horario_4 = ""
                    mare_altura_3 = ""
                
                # salva lista
                lista_infos.append([cidade, uf, tempo,
                                    temperatura, temperatura_max, temperatura_min,
                                    sensacao, nebulosidade, umidade, vento,
                                    ultra_violeta, coeficiente_mare,
                                    pesca, melhor_horario_pesca,
                                    mare_horario_1, mare_altura_1,
                                    mare_horario_2, mare_altura_2,
                                    mare_horario_3, mare_altura_3,
                                    mare_horario_4, mare_altura_4])

            # erro de execução
            except Exception as e:
                continue

        # fecha o driver
        driver.close()

        # cria o dataframe
        df_infos = pd.DataFrame(lista_infos,
                                columns=self.lista_colunas_tempo)
        
        # tratamentos adicionais
        df_infos['Temperatura_Max'] = df_infos[["Temperatura", "Temperatura_Max", "Temperatura_Min"]].max(axis=1)
        df_infos['Temperatura_Min'] = df_infos[["Temperatura", "Temperatura_Max", "Temperatura_Min"]].min(axis=1)
        
        # retorna resultados
        return df_infos
    
    
    def seleciona_conteudo_publicar(self, df_resultados):
        '''
        Seleciona conteúdo para publicar, de acordo com a estratégia implementada
        '''

        # estratéga de seleção de conteúdo
        df_selecionados = df_resultados.sample(10)
        
        # retorna resultados selecionados
        return df_selecionados
    
    
    def mapeia_conteudo_intent(self, df_linha):
        '''
        Mapeia conteúdo em um estado
        '''
        lista_estados = []
        
        ultra_violeta = df_linha['Ultra_Violeta']
        
        # índice ultra violeta máximo
        if ultra_violeta == 11:
            lista_estados.append(1)
        
        # índice ultra violeta
        else:
            lista_estados.append(2)
        
        # sorteia um dos elementos da lista
        estado = random.choice(lista_estados)
        return estado
        
    
    def atribui_template(self, df_linha, estado):
        '''
        Retorna template
        '''
        
        # campos principais
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
        pesca = df_linha['Pesca']
        melhor_horario_pesca = df_linha['Melhor_Horario_Pesca']
        
        # marés
        primeira_Mare_Horario = df_linha['1_Mare_Horario']
        primeira_Mare_Altura = df_linha['1_Mare_Altura']
        segunda_Mare_Horario = df_linha['2_Mare_Horario']
        segunda_Mare_Altura = df_linha['2_Mare_Altura']
        terceira_Mare_Horario = df_linha['3_Mare_Horario']
        terceira_Mare_Altura = df_linha['3_Mare_Altura']
        quarta_Mare_Horario = df_linha['4_Mare_Horario']
        quarta_Mare_Altura = df_linha['4_Mare_Altura']
        
        # início do texto
        inicio_texto = self.get_inicio_texto(cidade)
        
        # trocar depois
        estado = 2
        
        # Ultra Violeta
        if estado == 1:

            possibilidade_1 = f'''\
            Hoje {inicio_texto} {cidade} ({uf}) a previsão do tempo é de {tempo}, com uma temperatura de {temperatura}°C e sensação térmica de {sensacao_termica}°C.\nA temperatura máxima prevista é de {temperatura_max}°C e a mínima de {temperatura_min}°C.\nUtilize protetor solar durante o dia!
            '''
            
            possibilidade_2 = f'''\
            Hoje {inicio_texto} {cidade} ({uf}) a previsão do tempo é de {tempo}, com uma temperatura de {temperatura}°C e sensação térmica de {sensacao_termica}°C.\nO índice ultravioleta hoje está elevado ({ultra_violeta})!\nUtilize protetor solar, camiseta e óculos de sol! {self.twitter_api.dict_map_emoji['oculos_sol']}
            '''
            
            # lista de possibilidades para escolher
            lista_possibilidades = [possibilidade_1, possibilidade_2]
            tweet = random.choice(lista_possibilidades)
        
        
        # Não Ultra Violeta  
        elif estado == 2:
            
            possibilidade_1 = f'''\
            Hoje {inicio_texto} {cidade} ({uf}) a previsão do tempo é de {tempo}, com uma temperatura de {temperatura}°C e sensação térmica de {sensacao_termica}°C.\nA temperatura máxima prevista é de {temperatura_max}°C e a mínima de {temperatura_min}°C.
            '''
            
            possibilidade_2 = f'''\
            Hoje {inicio_texto} {cidade} ({uf}) a previsão do tempo é de {tempo}, com uma temperatura de {temperatura}°C e sensação térmica de {sensacao_termica}°C.\nA nebulosidade é de {nebulosidade}% e a velocidade do vento é de {vento} km/h.
            '''
            
            possibilidade_3 = f'''\
            Hoje {inicio_texto} {cidade} ({uf}) a previsão do tempo é de {tempo}, com uma temperatura de {temperatura}°C e sensação térmica de {sensacao_termica}°C.\n\nHorários de maré alta: {primeira_Mare_Horario} ({primeira_Mare_Altura}m) e {terceira_Mare_Horario}. ({terceira_Mare_Altura}m).\nHorários de maré baixa: {segunda_Mare_Horario} ({segunda_Mare_Altura}m) e {quarta_Mare_Horario}. ({quarta_Mare_Altura}m)
            '''
            
            possibilidade_4 = f'''\
            Hoje {inicio_texto} {cidade} ({uf}) a previsão do tempo é de {tempo}, com uma temperatura de {temperatura}°C e sensação térmica de {sensacao_termica}°C.\nO melhor horário para pescar é {melhor_horario_pesca} {self.twitter_api.dict_map_emoji['pesca']}.
            '''
            
            # lista de possibilidades para escolher
            lista_possibilidades = [possibilidade_1, possibilidade_2, possibilidade_3, possibilidade_4]
            tweet = random.choice(lista_possibilidades)
            
        else:
            return 0, ""
        
        # adiciona pós-processamentos ao tweet
        tweet = f"{self.twitter_api.get_inicio_post()}{tweet.strip()}{self.twitter_api.get_fim_post()}"
        
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
        
        # se não encontrar nada para publicar, retorna
        if (len(df_selecionados) == 0):
            return  
        
        # tenta publicar tweets
        for index in range(len(df_selecionados)):
            try:
                df_linha = df_selecionados.iloc[index]

                # estado (contexto) do conjunto de dados
                estado = self.mapeia_conteudo_intent(df_linha)

                # cria o tweet
                flag, tweet = self.atribui_template(df_linha, estado)

                # verifica se pode publicar o tweet
                if (flag == 0):
                    print ('tweet não pode ser publicado')
                    continue

                # verifica se tweet pode ser publicado
                if (self.twitter_api.verifica_tweet_pode_ser_publicado(tweet) and self.twitter_api.valida_tamanho_tweet(tweet)):
                    try:
                        self.twitter_api.make_tweet(tweet)
                        print ('Tweet publicado')

                        # espera um tempo para publicar novamente
                        time.sleep(self.tempo_espera_tweet_segundos)

                    except Exception as e:
                        print ('Não consegui publicar.')
                        print (f"Erro: {e}")

                # tweet não pode ser publicado
                else:
                    print ('tweet não pode ser publicado')

            # continua a execução
            except:
                continue