import pandas as pd
import numpy as np
import requests
import random
import urllib
import json
import time
import sys
import os
from datetime import date
import datetime
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
        
        # arquivos auxiliares
        self.path_infos_cidades='cidades.csv'
        self.path_bd = 'cidades_bd.csv'
        path_credenciais_user_agent = "credenciais_user_agent.json"
        path_intents = "intents.json"
        path_analisador_lexico = "analisador_lexico.json"
        
        # leitura do arquivo json com as credenciais
        try:
            f = open(path_credenciais_user_agent, mode="r")
            infos_login = json.load(f)
            self.user_agent = infos_login['user_agent']
            f.close()
        except:
            self.user_agent = {"user_agent":"temporary_agent"}
        
        # leitura do arquivo json com os intents
        f = open(path_intents, encoding='utf-8', mode="r")
        self.dict_intents = json.load(f)
        f.close()
        
        # leitura do arquivo json com o analisador léxico
        f = open(path_analisador_lexico, mode="r")
        dict_json_lexico = json.load(f)
        f.close()
        self.dict_analisador_lexico = {}
        self.lista_palavras_analisador_lexico = set()
        for chave, valor in dict_json_lexico.items():
            palavra = chave.split(']')[1].strip()
            numero = chave.split('numero=')[1].split(',')[0].strip()
            genero = chave.split('genero=')[1].split(']')[0].strip()
            chave = f"{palavra}|{numero}|{genero}"
            self.dict_analisador_lexico[chave] = valor.strip()
            self.lista_palavras_analisador_lexico.add(palavra)
        self.lista_palavras_analisador_lexico = list(self.lista_palavras_analisador_lexico)
        
        # parametros do webdriver
        self.chromeOptions = webdriver.ChromeOptions()
        self.chromeOptions.add_argument('--no-sandbox')
        self.chromeOptions.add_argument("--headless")
        self.chromeOptions.add_argument(f"User-Agent={self.user_agent}")
        
        # parâmetros
        self.url_tabua_mares = "https://www.tideschart.com"
        self.tempo_espera_tweet_segundos = 60
        self.qtd_cidades_selecionadas = 15
        self.qtd_min_dias_consecutivos = 10
        self.multiplicador_std = 1.3
        self.filler_tempo = 'céu nublado'
        self.modulo = 'tempo'
        
        # temperaturas max e min possíveis (validação conceitual)
        self.maior_temperatura_possivel = 55
        self.menor_temperatura_possivel = -10
        
        # icones
        self.icone_up = '▲'
        self.icone_down = '▼'
        
        # df cidades
        self.df_cidades = pd.read_csv(self.path_infos_cidades, encoding='latin-1', sep=';')
        
        # colunas para atribuir valor
        self.lista_colunas_tempo = ['cidade',
                                    'uf',
                                    'tempo',
                                    'temperatura',
                                    'temperatura_max',
                                    'temperatura_min',
                                    'nebulosidade',
                                    'umidade',
                                    'vento',
                                    'horario_por_sol',
                                    'pesca',
                                    'melhor_horario_pesca',
                                    'altura_maior_onda',
                                    'texto_onda',
                                    'url_imagem']
        
        # colunas para atribuir valor
        self.lista_colunas_salvar = ['cidade',
                                    'uf',
                                    'tempo',
                                    'temperatura',
                                    'temperatura_max',
                                    'temperatura_min',
                                    'nebulosidade',
                                    'umidade',
                                    'vento',
                                    'horario_por_sol',
                                    'pesca',
                                    'melhor_horario_pesca',
                                    'altura_maior_onda',
                                    'data']
        
        # se não existe arquivo de bd, cria
        if not os.path.exists(self.path_bd):
            pd.DataFrame(columns=self.lista_colunas_salvar).to_csv(self.path_bd, sep=';', index=False)
        
        # colunas de clima
        self.dict_map_clima = {'Overcast': 'céu nublado [emoji_nuvem]',
                               'Cloudy': 'céu nublado [emoji_nuvem]',
                               'Partly cloudy': 'céu parcialmente nublado [emoji_nuvem_sol]',
                               'Light rain shower': 'chuvas leves [emoji_chuva_sol]',
                               'Patchy rain possible': 'períodos de chuva ao longo do dia [emoji_chuva]',
                               'Moderate or heavy rain shower': 'chuvas fortes ao longo do dia [emoji_chuva_relampago]'}
        
        # colunas de clima
        self.dict_map_pesca = {'Today is an excellent fishing day': 'Excelente',
                               'Today is a good fishing day': 'Bom',
                               'Today is an average fishing day': 'Mediano'}
        
        # cidades
        self.lista_cidades_em = ['Rio de Janeiro']
        
        # path dos conteúdos do site
        self.path_url_imagem = '//*[@id="map"]'
        self.path_tempo1 = '//*[@id="main-content"]/div/div/div/div[1]/div[7]/div[1]/div/div[1]'
        self.path_temperatura1 = '//*[@id="main-content"]/div/div/div/div[1]/div[7]/div[2]/div/div[1]'
        self.path_temperatura_max_min1 = '//*[@id="main-content"]/div/div/div/div[1]/div[7]/div[2]/div/div[2]'
        self.path_nebulosidade1 = '//*[@id="main-content"]/div/div/div/div[1]/div[7]/div[1]/div/div[2]'
        self.path_umidade1 = '//*[@id="main-content"]/div/div/div/div[1]/div[7]/div[4]/div/div[1]'
        self.path_vento1 = '//*[@id="main-content"]/div/div/div/div[1]/div[7]/div[3]/div/div[1]'
        
        self.path_tempo2 = '//*[@id="main-content"]/div/div/div/div[1]/div[4]/div[1]/div/div[1]'
        self.path_temperatura2 = '//*[@id="main-content"]/div/div/div/div[1]/div[4]/div[2]/div/div[1]'
        self.path_temperatura_max_min2 = '//*[@id="main-content"]/div/div/div/div[1]/div[4]/div[2]/div/div[2]'
        self.path_nebulosidade2 = '//*[@id="main-content"]/div/div/div/div[1]/div[4]/div[1]/div/div[2]'
        self.path_umidade2 = '//*[@id="main-content"]/div/div/div/div[1]/div[4]/div[4]/div/div[1]'
        self.path_vento2 = '//*[@id="main-content"]/div/div/div/div[1]/div[4]/div[3]/div/div[1]'
        self.path_situacao_pesca1 = '//*[@id="main-content"]/div/div/div/div[1]/div[5]/div/h2/span'
        self.path_situacao_pesca2 = '//*[@id="main-content"]/div/div/div/div[1]/div[3]/div/h2/span'
        
        self.path_horario_por_sol = '//*[@id="main-content"]/div/div/div/div[1]/div[3]/div/div/table/tbody/tr[1]/td[7]'
        self.path_melhor_horario_pesca1 = '//*[@id="main-content"]/div/div/div/div[1]/div[5]/div/div/div[1]/div/h4'
        self.path_melhor_horario_pesca2 = '//*[@id="main-content"]/div/div/div/div[1]/div[5]/div/div/div[1]/div/h4[2]'
        self.path_por_sol = '//*[@id="main-content"]/div/div/div/div[1]/div[3]/div/div/table/tbody/tr[1]/td[7]'
        self.path_mare1 = '//*[@id="main-content"]/div/div/div/div[1]/div[3]/div/div/table/tbody/tr[1]/td[2]'
        self.path_mare2 = '//*[@id="main-content"]/div/div/div/div[1]/div[3]/div/div/table/tbody/tr[2]/td[3]'
        self.path_mare3 = '//*[@id="main-content"]/div/div/div/div[1]/div[3]/div/div/table/tbody/tr[1]/td[4]'
        self.path_mare4 = '//*[@id="main-content"]/div/div/div/div[1]/div[3]/div/div/table/tbody/tr[1]/td[5]'

    
    def trata_mare(self, elemento):
        '''
        trata maré
        '''
        horario = (elemento.split('m')[0] + 'm').strip()
        altura = float(elemento.split(' ')[1].strip())
        simbolo = elemento.split(' ')[0][-1].strip()
        
        if simbolo == self.icone_up:
            simbolo = 'up'
        else:
            simbolo = 'down'
        return (horario, altura, simbolo)
        
    
    def get_analisador_lexico(self, palavra, numero, genero):
        '''
        Retorna início do texto para publicação
        '''
        return (self.dict_analisador_lexico[f"{palavra}|{numero}|{genero}"])
        
        
    def count_dias(self, data_hoje, lista_datas):
        '''
        retorna qtd de dias consecutivos
        '''
        qtd_dias = 0
        data = data_hoje
        while (True):
            data = data - datetime.timedelta(1)
            if data.strftime("%d/%m/%Y") in lista_datas:
                qtd_dias+=1
            else:
                break

        return qtd_dias


    def count_valor(self, valor_hoje, lista_valores, tipo_operacao):
        '''
        retorna qtd de dias onde o valor satisfaz determinada condição
        '''
        qtd_dias = 0

        if tipo_operacao == 'maior':
            for valor in lista_valores:
                if (valor_hoje > valor):
                    qtd_dias +=1
                else:
                    break

        elif tipo_operacao == 'menor':
            for valor in lista_valores:
                if (valor_hoje < valor):
                    qtd_dias +=1
                else:
                    break

        else:
            return 0

        # compara com mínimo
        if (qtd_dias < self.qtd_min_dias_consecutivos):
            return 0

        # retorna qtd de dias
        return qtd_dias
    
    
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
                time.sleep(2)

                # leitura do conteúdo
                try:
                    tempo = driver.find_element_by_xpath(self.path_tempo1).text
                except:
                    try:
                        tempo = driver.find_element_by_xpath(self.path_tempo2).text
                    except Exception as e:
                        print (f'Erro na cidade {cidade}! {e}')
                        continue
                    
                try:
                    temperatura = int((driver.find_element_by_xpath(self.path_temperatura1).text).split('°C')[0])
                except:
                    try:
                        temperatura =  int((driver.find_element_by_xpath(self.path_temperatura2).text).split('°C')[0])
                    except Exception as e:
                        print (f'Erro na cidade {cidade}! {e}')
                        continue
                    
                          
                try:
                    temperatura_max_min = driver.find_element_by_xpath(self.path_temperatura_max_min1).text
                except:
                    try:
                        temperatura_max_min = driver.find_element_by_xpath(self.path_temperatura_max_min2).text
                    except Exception as e:
                        print (f'Erro na cidade {cidade}! {e}')
                        continue
                    
                try:
                    nebulosidade = int(driver.find_element_by_xpath(self.path_nebulosidade1).text.split('Cloud cover ')[1].split('%')[0])
                except:
                    try:
                        nebulosidade = int(driver.find_element_by_xpath(self.path_nebulosidade2).text.split('Cloud cover ')[1].split('%')[0])
                    except Exception as e:
                        print (f'Erro na cidade {cidade}! {e}')
                        continue
                    
                
                try:
                    umidade = int(driver.find_element_by_xpath(self.path_umidade1).text.split('%')[0])
                except:
                    try:
                        umidade = int(driver.find_element_by_xpath(self.path_umidade2).text.split('%')[0])
                    except Exception as e:
                        print (f'Erro na cidade {cidade}! {e}')
                        continue
                     
                    
                try:
                    vento = int(driver.find_element_by_xpath(self.path_vento1).text.split(' ')[0])
                except:
                    try:
                        vento = int(driver.find_element_by_xpath(self.path_vento2).text.split(' ')[0])
                    except Exception as e:
                        print (f'Erro na cidade {cidade}! {e}')
                        continue
                    
                try:
                     pesca = driver.find_element_by_xpath(self.path_situacao_pesca1).text
                except:
                    try:
                        pesca = driver.find_element_by_xpath(self.path_situacao_pesca2).text
                    except Exception as e:
                        print (f'Erro na cidade {cidade}! {e}')
                        continue
                    
    
                # melhor horário de pesca
                try:
                    melhor_horario_pesca = driver.find_element_by_xpath(self.path_melhor_horario_pesca2).text.split('From ')[1].replace(' to ', ' - ')
                except:
                    try:
                        melhor_horario_pesca = driver.find_element_by_xpath(self.path_melhor_horario_pesca1).text.split('From ')[1].replace(' to ', ' - ')
                    except Exception as e:
                        print (f'Erro na cidade {cidade}! {e}')
                        continue
                   
                        
                # por do sol
                horario_por_sol = str(driver.find_element_by_xpath(self.path_horario_por_sol).text).split(' ')[1].strip()
                
                # marés
                try:
                    horario_mare_1, altura_mare_1, simbolo_mare_1 = self.trata_mare(driver.find_element_by_xpath(self.path_mare1).text)
                except:
                    horario_mare_1 = ""
                    altura_mare_1 = -1
                    simbolo_mare_1 = ""
                    
                try:
                    horario_mare_2, altura_mare_2, simbolo_mare_2 = self.trata_mare(driver.find_element_by_xpath(self.path_mare2).text)
                except:
                    horario_mare_2 = ""
                    altura_mare_2 = -1
                    simbolo_mare_2 = ""
                    
                try:
                    horario_mare_3, altura_mare_3, simbolo_mare_3 = self.trata_mare(driver.find_element_by_xpath(self.path_mare3).text)
                except:
                    horario_mare_3 = ""
                    altura_mare_3 = -1
                    simbolo_mare_3 = ""
                
                try:
                    horario_mare_4, altura_mare_4, simbolo_mare_4 = self.trata_mare(driver.find_element_by_xpath(self.path_mare4).text)
                
                except:
                    horario_mare_4 = ""
                    altura_mare_4 = -1
                    simbolo_mare_4 = ""
                    
                # altura da maior onda
                altura_maior_onda = str(max(altura_mare_1, altura_mare_2, altura_mare_3, altura_mare_4))
                
                # texto onda
                if (simbolo_mare_1 == ""):
                    continue
                
                elif (simbolo_mare_1 == "up" and simbolo_mare_2 == ""):
                     texto_onda = f"Horário de maré alta: {horario_mare_1} ({altura_mare_1}m)"
                        
                elif (simbolo_mare_1 == "down" and simbolo_mare_2 == ""):
                     texto_onda = f"Horário de maré baixa: {horario_mare_1} ({altura_mare_1}m)"
                              
                elif (simbolo_mare_1 == 'up' and simbolo_mare_4 != ""):
                    
                    texto_onda = f"Horários de maré alta: {horario_mare_1} ({altura_mare_1}m) e {horario_mare_3} ({altura_mare_3}m).\nHorários de maré baixa: {horario_mare_2} ({altura_mare_2}m) e {horario_mare_4} ({altura_mare_4}m)"
                
                elif (simbolo_mare_1 == 'up' and simbolo_mare_4 == ""):
                    texto_onda = f"Horários de maré alta: {horario_mare_1} ({altura_mare_1}m) e {horario_mare_3} ({altura_mare_3}m).\nHorário de maré baixa: {horario_mare_2} ({altura_mare_2}m)"
                    
                elif (simbolo_mare_1 == 'down' and simbolo_mare_4 != ""):
                    
                    texto_onda = f"Horário de maré alta: {horario_mare_2} ({altura_mare_2}m) e {horario_mare_4} ({altura_mare_4}m).\nHorários de maré baixa: {horario_mare_1} ({altura_mare_1}m) e {horario_mare_3} ({altura_mare_3}m)"
                
                elif (simbolo_mare_1 == 'down' and simbolo_mare_4 == ""):
                    texto_onda = f"Horário de maré alta: {horario_mare_2} ({altura_mare_2}m).\nHorários de maré baixa: {horario_mare_1} ({altura_mare_1}m) e {horario_mare_3} ({altura_mare_3}m)"
                    
                else:
                    continue
                  
                # temperatura max
                temperatura_max = int(temperatura_max_min.split('Min ')[1].split('°')[0])
                
                # temperatura min
                temperatura_min = int(temperatura_max_min.split('Max ')[1].split('°')[0])
                
                # validação conceitual de temperaturas
                maior_valor_temperatura = max([temperatura, temperatura_max, temperatura_min])
                menor_valor_temperatura = min([temperatura, temperatura_max, temperatura_min])                         

                # se estiver fora da range, ignora a cidade e continua o processo
                if (maior_valor_temperatura > self.maior_temperatura_possivel or menor_valor_temperatura < self.menor_temperatura_possivel):
                    continue
                    
                # mapeia tempo
                if tempo in self.dict_map_clima.keys():
                    try:
                        tempo = self.dict_map_clima[tempo]
                    except:
                        tempo = self.filler_tempo
                else:
                    tempo = self.filler_tempo
                     
                # mapeia pesca
                if pesca in self.dict_map_pesca.keys():
                    try:
                        pesca = self.dict_map_pesca[pesca]
                    except:
                        pesca = ''
                else:
                    pesca = ''
                      
                    
                # imagem adicional do litoral da cidade
                url_imagem = driver.find_element_by_xpath(self.path_url_imagem).get_attribute("src")
                
                # salva lista
                lista_infos.append([cidade,
                                    uf,
                                    tempo,
                                    temperatura,
                                    temperatura_max,
                                    temperatura_min,
                                    nebulosidade,
                                    umidade,
                                    vento,
                                    horario_por_sol,
                                    pesca,
                                    melhor_horario_pesca,
                                    altura_maior_onda,
                                    texto_onda,
                                    url_imagem])

            # erro de execução
            except Exception as e:
                print (f'Erro na cidade {cidade}! {e}')
                continue

        # fecha o driver
        driver.close()
                                                  
        # cria o dataframe
        try:
            df_infos = pd.DataFrame(lista_infos,
                                    columns=self.lista_colunas_tempo)

            # tratamentos adicionais
            df_infos['temperatura_max'] = df_infos[["temperatura", "temperatura_max", "temperatura_min"]].max(axis=1)
            df_infos['temperatura_min'] = df_infos[["temperatura", "temperatura_max", "temperatura_min"]].min(axis=1)

            # transforma tudo em string
            for column in df_infos.columns.tolist():
                df_infos[column] = df_infos[column].astype(str)
                
            # inclui data de hoje
            df_infos['data'] = date.today().strftime("%d/%m/%Y")

            # retorna resultados
            return df_infos
        
        # erro de execução
        except Exception as e:
            print (f'Erro no fim do processo! {e}')
            sys.exit(0)

     
    def seleciona_conteudo_publicar(self, df_resultados):
        '''
        Seleciona conteúdo para publicar, de acordo com a estratégia implementada
        '''

        try:
            # estratéga de seleção de conteúdo
            max_observacoes = min(len(df_resultados), self.qtd_cidades_selecionadas)
            df_selecionados = df_resultados.sample(max_observacoes)

            # retorna resultados selecionados
            return df_selecionados
        except:
            sys.exit(0)
    

    def atribui_intent(self, df_linha):
        '''
        retorna intent com base no conteúdo
        '''
        try:
            # campos principais
            cidade = df_linha['cidade']
            uf = df_linha['uf']
            tempo = df_linha['tempo']
            temperatura = int(df_linha['temperatura'])
            temperatura_max = int(df_linha['temperatura_max'])
            temperatura_min = int(df_linha['temperatura_min'])
            nebulosidade = int(df_linha['nebulosidade'])
            umidade = int(df_linha['umidade'])
            vento = int(df_linha['vento'])
            pesca = df_linha['pesca']
            altura_maior_onda = float(df_linha['altura_maior_onda'])
            
            # flag
            qtd_dias_temperatura_max = int(df_linha["qtd_dias_temperatura_max"])
            qtd_dias_temperatura_min = int(df_linha["qtd_dias_temperatura_min"])
            qtd_dias_nebulosidade_max = int(df_linha["qtd_dias_nebulosidade_max"])
            qtd_dias_umidade_max = int(df_linha["qtd_dias_umidade_max"])
            qtd_dias_vento_max = int(df_linha["qtd_dias_vento_max"])
            qtd_dias_onda_max = int(df_linha["qtd_dias_onda_max"])
            flag_outlier_temperatura = int(df_linha["flag_outlier_temperatura"])

            ##################
            # Valores outlier
            ##################
            
            # temperatura maxima
            if qtd_dias_temperatura_max > 0:
                return "TEMPERATURA_MAXIMA"
            
            # temperatura minima
            if qtd_dias_temperatura_min > 0:
                return "TEMPERATURA_MINIMA"
            
            # nebulosidade maxima
            if qtd_dias_nebulosidade_max > 0:
                return "NEBULOSIDADE_MAXIMA"
            
            # umidade maxima
            if qtd_dias_umidade_max > 0:
                return "UMIDADE_MAXIMA"
            
            # vento maxima
            if qtd_dias_vento_max > 0:
                return "VENTO_MAXIMA"
            
            if qtd_dias_onda_max > 0:
                return "ONDA_MAXIMA"
            
            # muito bom para pescar
            if pesca == "Excelente":
                return "BOM_PESCAR"
            
            # mar não está para peixes
            if (pesca not in ["Excelente", "Bom"] and altura_maior_onda > 1.6):
                return "MAR_NAO_ESTA_PARA_PEIXES"
            
            # sol ultravioleta
            if temperatura > 32:
                return "SOL_ULTRAVIOLETA"
            
            if flag_outlier_temperatura == 1:
                return "TEMPERATURA_ALTA_OUTLIER"
            
            if flag_outlier_temperatura == -1:
                return "TEMPERATURA_BAIXA_OUTLIER"
            
            ##################
            # Valores altos
            ##################
            
            # umidade alta
            if umidade >= 95:
                return "UMIDADE_ALTA"

            # nebulosidade alta
            if nebulosidade >= 90:
                return "NEBULOSIDADE_ALTA"

            # vento alto
            if vento >= 32:
                return "VENTO_ALTO"
            
            if (temperatura == temperatura_max and temperatura_max == temperatura_min):
                return "TEMP_IGUAIS"

            # se não caiu em nenhum caso, retorna comportamento usual
            return 'NORMAL'
            
        except Exception as e:
                print (f'Erro! {e}')
                return ""
    
    def atribui_template(self, df_linha, intent):
        '''
        Retorna template
        '''
        print (f'Intent: {intent}')
        
        try:
            # campos principais
            cidade = df_linha['cidade']
            uf = df_linha['uf']
            tempo = df_linha['tempo']
            temperatura = df_linha['temperatura']
            temperatura_max = df_linha['temperatura_max']
            temperatura_min = df_linha['temperatura_min']
            nebulosidade = df_linha['nebulosidade']
            umidade = df_linha['umidade']
            vento = df_linha['vento']
            pesca = df_linha['pesca']
            melhor_horario_pesca = df_linha['melhor_horario_pesca']
            horario_por_sol = df_linha['horario_por_sol']
            altura_maior_onda = df_linha['altura_maior_onda']
            texto_onda = df_linha['texto_onda']
            
            # flags
            qtd_dias_consecutivos = df_linha['qtd_dias_consecutivos']
            qtd_dias_temperatura_max = df_linha['qtd_dias_temperatura_max']
            qtd_dias_temperatura_min = df_linha['qtd_dias_temperatura_min']
            qtd_dias_nebulosidade_max = df_linha['qtd_dias_nebulosidade_max']
            qtd_dias_umidade_max = df_linha['qtd_dias_umidade_max']
            qtd_dias_vento_max = df_linha['qtd_dias_vento_max']
            qtd_dias_onda_max = df_linha['qtd_dias_onda_max']

            # início do texto
            if cidade in self.lista_cidades_em:
                numero = "singular"
                genero = "masculino"
            else:
                numero = "singular"
                genero = "neutro"

            # lista de textos possíveis para cada intent
            lista_possibilidades = self.dict_intents[intent]
            
            # seleciona texto
            texto_selecionado = random.choice(lista_possibilidades).strip()
            
            # dicionário para substituição de campos
            dicionario_map = {
                              "[cidade]":cidade,
                              "[uf]":uf,
                              "[tempo]":tempo,
                              "[temperatura]":temperatura,
                              "[temperatura_max]":temperatura_max,
                              "[temperatura_min]":temperatura_min,
                              "[nebulosidade]":nebulosidade,
                              "[umidade]":umidade,
                              "[vento]":vento,
                              "[pesca]":pesca,
                              "[melhor_horario_pesca]":melhor_horario_pesca,
                              "[horario_por_sol]":horario_por_sol,
                              "[texto_onda]":texto_onda,
                              "[altura_maior_onda]":altura_maior_onda,
                                
                              "[qtd_dias_temperatura_max]":qtd_dias_temperatura_max,
                              "[qtd_dias_temperatura_min]":qtd_dias_temperatura_min,
                              "[qtd_dias_nebulosidade_max]":qtd_dias_nebulosidade_max,
                              "[qtd_dias_umidade_max]":qtd_dias_umidade_max,
                              "[qtd_dias_vento_max]":qtd_dias_vento_max,
                              "[qtd_dias_onda_max]":qtd_dias_onda_max,
                
                             }
            
            # aplica substituições no template
            for key, value in dicionario_map.items():
                texto_selecionado = texto_selecionado.replace(key, value)
                
            # aplica analisador léxico
            for palavra in self.lista_palavras_analisador_lexico:
                valor = self.get_analisador_lexico(palavra, numero, genero)
                texto_selecionado = texto_selecionado.replace(f"[{palavra}]", valor)
            
            # adiciona pós-processamentos ao tweet
            tweet = f"{self.twitter_api.get_inicio_post()}{texto_selecionado.strip()}{self.twitter_api.get_fim_post()}"

            return tweet
        
        
        except Exception as e:
            print (f'Erro! {e}')
            return ""
    
    def popula_estatisticas(self, df_selecionados, df_atual):
        '''
        popula df selecionado com estatísticas envolendo df atual
        '''
                  
        data_hoje = date.today()
        lista_cidades = list(set(df_selecionados['cidade']))
        lista_retorno = []
        
        # se df estiver vazio...
        if (len(df_atual) == 0):
            # itera cidades
            for cidade in lista_cidades:
                lista_valores = [cidade, 0, 0, 0, 0, 0, 0, 0, 0]
                lista_retorno.append(lista_valores)
            
            
        # se não estiver vazio...
        else:

            df_atual['data_formatada'] = pd.to_datetime(df_atual['data'])
            df_passado = df_atual.loc[(df_atual['data_formatada'] < pd.to_datetime(data_hoje))]
        

            # itera cidades
            for cidade in lista_cidades:
                df_cidade = df_passado.loc[(df_passado['cidade'] == cidade)]
                lista_datas = set(df_cidade['data'])
                qtd_dias = self.count_dias(data_hoje, lista_datas)

                df_valores_cidade = df_selecionados.loc[(df_selecionados['cidade'] == cidade)]

                # se poucos dias, retorna 0
                if (qtd_dias < self.qtd_min_dias_consecutivos):
                    lista_valores = [cidade, 0, 0, 0, 0, 0, 0, 0, 0]
                    lista_retorno.append(lista_valores)
                    continue

                # filtra datas consecutivas
                data_ultima = data_hoje - datetime.timedelta(qtd_dias)
                data_ultima = data_ultima.strftime("%d/%m/%Y")
                df_cidade = df_cidade.loc[df_cidade['data_formatada'] >= data_ultima].sort_values(by=['data_formatada'], ascending=False) 

                # valores computados
                qtd_dias_temperatura_max = self.count_valor(float(df_valores_cidade['temperatura']), df_cidade['temperatura'].values.tolist(), 'maior')
                qtd_dias_temperatura_min = self.count_valor(float(df_valores_cidade['temperatura']), df_cidade['temperatura'].values.tolist(), 'menor')
                qtd_dias_nebulosidade_max = self.count_valor(float(df_valores_cidade['nebulosidade']), df_cidade['nebulosidade'].values.tolist(), 'maior')
                qtd_dias_umidade_max = self.count_valor(float(df_valores_cidade['umidade']), df_cidade['umidade'].values.tolist(), 'maior')
                qtd_dias_vento_max = self.count_valor(float(df_valores_cidade['vento']), df_cidade['vento'].values.tolist(), 'maior')
                qtd_dias_onda_max = self.count_valor(float(df_valores_cidade['altura_maior_onda']), df_cidade['altura_maior_onda'].values.tolist(), 'maior')
                
                # outliers
                temperatura_media = df_cidade['temperatura'].mean()
                temperatura_std = df_cidade['temperatura'].std()
                temp_max = temperatura_media + (temperatura_std * self.multiplicador_std)
                temp_min = temperatura_media - (temperatura_std * self.multiplicador_std)
                
                if (df_valores_cidade['temperatura'] > temp_max):
                    flag_outlier_temperatura = 1
                elif (df_valores_cidade['temperatura'] < temp_min):
                    flag_outlier_temperatura = -1
                else:
                    flag_outlier_temperatura = 0

                lista_valores = [cidade,
                                 qtd_dias,
                                 qtd_dias_temperatura_max,
                                 qtd_dias_temperatura_min,
                                 qtd_dias_nebulosidade_max,
                                 qtd_dias_umidade_max,
                                 qtd_dias_vento_max,
                                 qtd_dias_onda_max,
                                 flag_outlier_temperatura]

                lista_retorno.append(lista_valores)

        
        # estatísticas
        df_estatisticas = pd.DataFrame(lista_retorno, columns=['cidade',
                                                               'qtd_dias_consecutivos',
                                                               'qtd_dias_temperatura_max',
                                                               'qtd_dias_temperatura_min',
                                                               'qtd_dias_nebulosidade_max',
                                                               'qtd_dias_umidade_max',
                                                               'qtd_dias_vento_max',
                                                               'qtd_dias_onda_max',
                                                               'flag_outlier_temperatura'])
        
        # transforma dados em string
        df_estatisticas['qtd_dias_consecutivos'] = df_estatisticas['qtd_dias_consecutivos'].astype(str)
        df_estatisticas['qtd_dias_temperatura_max'] = df_estatisticas['qtd_dias_temperatura_max'].astype(str)
        df_estatisticas['qtd_dias_temperatura_min'] = df_estatisticas['qtd_dias_temperatura_min'].astype(str)
        df_estatisticas['qtd_dias_nebulosidade_max'] = df_estatisticas['qtd_dias_nebulosidade_max'].astype(str)
        df_estatisticas['qtd_dias_umidade_max'] = df_estatisticas['qtd_dias_umidade_max'].astype(str)
        df_estatisticas['qtd_dias_vento_max'] = df_estatisticas['qtd_dias_vento_max'].astype(str)
        df_estatisticas['qtd_dias_onda_max'] = df_estatisticas['qtd_dias_onda_max'].astype(str)
        df_estatisticas['flag_outlier_temperatura'] = df_estatisticas['flag_outlier_temperatura'].astype(str)
        
        return df_estatisticas
         
        
    def publica_conteudo(self):
        '''
        Publica previsão do tempo (tábua de marés)
        '''
        
        # data de hoje
        data_hoje = date.today().strftime("%d_%m_%Y")
        
        try:
            # gera resultados
            df_resultados = self.gera_df_tabua_mares()
            
            # salva resultados na pasta
            df_resultados[self.lista_colunas_salvar].to_csv(f"resultados_cidades/{data_hoje}.csv", index=False, sep=';')
            
            # adiciona dados da rodada ao BD
            df_atual = pd.read_csv(self.path_bd, sep=';')
            df_atual = df_atual.loc[(df_atual['data'] != date.today().strftime("%d/%m/%Y")) & (~df_atual['cidade'].isnull())]
            df_novo = df_atual.append(df_resultados[self.lista_colunas_salvar])
            df_novo.to_csv(self.path_bd, index=False, sep=';')

            # filtra dados para publicação
            df_selecionados = self.seleciona_conteudo_publicar(df_resultados)
        
        except:
            sys.exit(0)
        
        # se não encontrar nada para publicar, encerra execução
        try:
            if (len(df_selecionados) == 0):
                sys.exit(0)
        except:
            sys.exit(0)
            
        # popula resultados com estatísticas
        df_estatisticas = self.popula_estatisticas(df_selecionados, df_atual)
        
        # junta tabelas
        df_selecionados = pd.merge(df_selecionados, df_estatisticas, how='left', on='cidade')
                        
        # verifica se pode publicar conteúdo
        if (self.twitter_api.get_status_twitter() != 1):
            print ("Flag 0. Não posso publicar!")
            return
        
        # tenta publicar tweets, um por um
        for index in range(len(df_selecionados)):
            try:
                df_linha = df_selecionados.iloc[index]
                
                # salva foto
                with open("foto.png", "wb") as f:
                    f.write(requests.get(df_linha['url_imagem'], headers={'User-Agent': self.user_agent}).content)
                time.sleep(1)

                # intent do conjunto de dados
                intent = self.atribui_intent(df_linha)
                if (intent == ""):
                    print ('intent vazio. tweet não pode ser publicado.')
                    continue

                # cria o tweet
                tweet = self.atribui_template(df_linha, intent)
                print (tweet)

                # verifica se pode publicar o tweet
                if (tweet == ""):
                    print ('tweet vazio. tweet não pode ser publicado.')
                    continue

                # verifica se tweet pode ser publicado                
                if (self.twitter_api.valida_tweet(tweet)):
                    try:
                        self.twitter_api.make_tweet(tweet, self.modulo, 'foto')
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
            except Exception as e:
                print (f"Erro na publicação! {e}")
                continue