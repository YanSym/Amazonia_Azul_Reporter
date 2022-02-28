import pandas as pd
import numpy as np
import random
import shutil
import time
import json
import cv2
import sys
import os
import datetime
import unidecode
from PIL import Image
from datetime import date
from selenium import webdriver
from discourse_ordering import DiscourseOrderingClass
from twitter_api import TwitterClass

class ImagensClass:
    """
    Classe de imagens de satélite
    """
    def __init__(self):
        
        # path do chromedriver
        self.path_to_chromedriver = 'chromedriver'
        
        # API do Twitter
        self.twitter_api = TwitterClass()
        
        # arquivos auxiliares
        self.path_infos_portos="portos.csv"
        self.path_bd = "portos_bd.csv"
        path_intents = "intents.json"
        path_analisador_lexico = "analisador_lexico.json"
        self.discourse_ordering_object = DiscourseOrderingClass()
        
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
        
        # parâmetros
        self.tempo_espera_tweet_segundos = 60
        self.qtd_cidades_selecionadas = 5
        self.qtd_min_dias_consecutivos = 10
        self.max_tentativas = 10
        self.multiplicador_std = 1.3
        self.modulo = 'imagens'
        
        # qtd de navios max e min possíveis (validação conceitual)
        self.maior_qtd_navios = 1_000
        self.menor_qtd_navios = 2
        
        # df portos
        self.df_portos = pd.read_csv(self.path_infos_portos, encoding='latin-1', sep=';')
        
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
        
        # colunas para atribuir valor
        self.lista_colunas = ['cidade',
                              'uf',
                              'qtd_navios_porto',
                              'qtd_navios_chegando',
                              'status']
        
        # colunas para salvar
        self.lista_colunas_salvar = ['cidade',
                                     'uf',
                                     'qtd_navios_porto',
                                     'qtd_navios_chegando',
                                     'status',
                                     'data']
        
        # se não existe arquivo de bd, cria
        if not os.path.exists(self.path_bd):
            pd.DataFrame(columns=self.lista_colunas_salvar).to_csv(self.path_bd, sep=';', index=False)
        
        # cidades
        self.lista_cidades_em = ['Rio de Janeiro']
        
        # path dos conteúdos do site
        self.path_qtd_navios_porto = '//*[@id="generalInfo"]/div[2]/div/div/div/div/p[3]/b/a'
        self.path_qtd_navios_chegando = '//*[@id="generalInfo"]/div[2]/div/div/div/div/p[4]/b/a'
        
        # data de hoje
        self.data_hoje = self.get_dia_atual()
        

    def clica_botao(self, driver, xpath):
        '''
        clica em um elemento da página e espera
        '''
        driver.find_element_by_xpath(xpath).click()
        time.sleep(5)

        
    def move_offset(self, webdriver):
        '''
        move o mouse
        '''
        try:
            action = webdriver.ActionChains(driver)
            action.move_by_offset(10, 20)
            action.perform()
        except:
            pass

        
    def fecha_add(self, driver):
        '''
        fecha propagandas do site
        '''
        try:
            # fecha add 1
            driver.find_element_by_xpath('//*[@id="leadinModal-405037"]/div[2]/button').click()
            time.sleep(3)

            # fecha add 2
            driver.find_element_by_xpath('//*[@id="div-gpt-ad-1539340679150-0"]').click()
            time.sleep(3)
        except:
            pass
        

    # botao de accept
    def clica_accept(self, driver):
        '''
        tenta clicar na mensagem de aceitar
        '''
        try:
            driver.find_element_by_xpath('//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]').click()
            time.sleep(3)
        except:
            pass
        

    # salva screenshot
    def salva_screenshot(self, driver, imagem):
        '''
        salva screenshot da tela
        '''
        screenshot = driver.save_screenshot(imagem)
        img = cv2.imread(imagem)
        img = cv2.resize(img, (1000, 500))
        cv2.imwrite(imagem, img)

        img = Image.open(imagem)
        crop_dim = (60, 60, 700, 440)
        cropped_img = img.crop(crop_dim)
        cropped_img.save(imagem)
    
    
    def get_dia_atual(self):
        '''
        data de hoje
        '''
        # data de hoje
        dia = str(int(date.today().strftime("%d")))
        mes = self.dict_map_mes[int(date.today().strftime("%m"))]
        ano = str(int(date.today().strftime("%Y")))
        return f"{dia} de {mes} de {ano}"
    
    
    def extrai_imagem_site(self, driver, cidade):
        '''
        extrai a imagem do site
        '''
        try:
            # botao de accept
            self.clica_accept(driver)

            # abre layers
            self.clica_botao(driver, '//*[@id="svg_icon_layers"]')

            # tipo de mapa
            self.clica_botao(driver, '//*[@id="baseLayerSelect"]')

            # mapa tipo satelite
            self.clica_botao(driver, '//*[@id="baseLayerSelect"]/option[3]')

            # fecha layers
            self.clica_botao(driver, '//*[@id="map_area_outer"]/div[2]/div[1]/div/div[1]/div[9]/div[1]')

            # fecha add
            self.fecha_add(driver)

            # move offset
            self.move_offset(webdriver)

            # botao de accept
            self.clica_accept(driver)
            
            # salva screenshot
            self.salva_screenshot(driver, f'imagens/img_satelite_{unidecode.unidecode(cidade)}.png')

            return 1
        
        except Exception as e:
            print (f'Sem Imagem. {e}')
            return 0

        
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
    
    
    def gera_df_navios(self):
        '''
        Gera resultados
        '''
    
        lista_infos = []

        # itera cidades
        for index, row in self.df_portos.iterrows():
            
            try:
                cidade = row['Cidade']
                uf = row['UF']
                url1 = row['URL1']
                url2 = row['URL2']
                    
                # entra na url 1
                driver = webdriver.Chrome(self.path_to_chromedriver, options=self.chromeOptions)
                driver.get(url1)
                time.sleep(10)
                
                # imagem de satelite
                status = self.extrai_imagem_site(driver, cidade)
                driver.close()
               
                # entra na url 2
                driver = webdriver.Chrome(self.path_to_chromedriver, options=self.chromeOptions)
                driver.get(url2)
                time.sleep(10)
                    
                # quantidade de navios no porto e chegando
                qtd_navios_porto = int(driver.find_element_by_xpath(self.path_qtd_navios_porto).text)
                qtd_navios_chegando = int(driver.find_element_by_xpath(self.path_qtd_navios_chegando).text)
                
                # verifica outliers
                if (qtd_navios_porto > self.maior_qtd_navios or qtd_navios_chegando > self.maior_qtd_navios or\
                    qtd_navios_porto < self.menor_qtd_navios or qtd_navios_chegando < self.menor_qtd_navios):
                    continue
                
                # salva lista
                lista_infos.append([cidade,
                                    uf,
                                    qtd_navios_porto,
                                    qtd_navios_chegando,
                                    status])
                driver.close()

            # erro de execução
            except Exception as e:
                print (f'Erro na cidade {cidade}! {e}')
                print(driver.page_source)
                driver.close()
                continue
                                                  
        # cria o dataframe
        try:
            df_infos = pd.DataFrame(lista_infos,
                                    columns=self.lista_colunas)

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
            qtd_navios_porto = df_linha['qtd_navios_porto']
            qtd_navios_chegando = int(df_linha['qtd_navios_chegando'])
            
            # flag
            qtd_dias_consecutivos = int(df_linha["qtd_dias_consecutivos"])
            qtd_navios_porto_max = int(df_linha["qtd_navios_porto_max"])
            qtd_navios_porto_min = int(df_linha["qtd_navios_porto_min"])
            flag_outlier = int(df_linha["flag_outlier"])
            
            # navios maxima
            if qtd_navios_porto_max > 0:
                return "NAVIOS_MAXIMA"
            
            # navios minima
            if qtd_navios_porto_min > 0:
                return "NAVIOS_MINIMA"
            
            # navios minima
            if flag_outlier > 0:
                return "NAVIOS_ALTA"
            
            # modo usual
            return "REPORT_NAVIOS"
            
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
            qtd_navios_porto = df_linha['qtd_navios_porto']
            qtd_navios_chegando = df_linha['qtd_navios_chegando']

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
                              "[qtd_navios_porto]":qtd_navios_porto,
                              "[qtd_navios_chegando]":qtd_navios_chegando,
                              "[data_hoje]":self.data_hoje
                             }
            
            # aplica substituições no template
            for key, value in dicionario_map.items():
                texto_selecionado = texto_selecionado.replace(key, value)
                
            # aplica analisador léxico
            for palavra in self.lista_palavras_analisador_lexico:
                valor = self.get_analisador_lexico(palavra, numero, genero)
                texto_selecionado = texto_selecionado.replace(f"[{palavra}]", valor)
                
            # atribui ordenação do discurso (discourse ordering)
            texto_selecionado = self.discourse_ordering_object.discourse_ordering(intent, texto_selecionado)
            
            # adiciona pós-processamentos ao tweet
            tweet = f"{self.twitter_api.get_inicio_post()}{texto_selecionado.strip()}\n\nFonte: MarineTraffic{self.twitter_api.get_fim_post()}"

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
                lista_valores = [cidade, 0, 0, 0, 0]
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
                    lista_valores = [cidade, 0, 0, 0, 0]
                    lista_retorno.append(lista_valores)
                    continue

                # filtra datas consecutivas
                data_ultima = data_hoje - datetime.timedelta(qtd_dias)
                data_ultima = data_ultima.strftime("%d/%m/%Y")
                df_cidade = df_cidade.loc[df_cidade['data_formatada'] >= data_ultima].sort_values(by=['data_formatada'], ascending=False) 

                # valores computados
                qtd_navios_max = self.count_valor(float(df_valores_cidade['qtd_navios_porto']), df_cidade['qtd_navios_porto'].values.tolist(), 'maior')
                qtd_navios_min = self.count_valor(float(df_valores_cidade['qtd_navios_porto']), df_cidade['qtd_navios_porto'].values.tolist(), 'menor')
                
                # outliers
                navios_media = df_cidade['qtd_navios_porto'].mean()
                navios_std = df_cidade['qtd_navios_porto'].std()
                
                navios_max = navios_media + (navios_std * self.multiplicador_std)
                navios_min = navios_media - (navios_std * self.multiplicador_std)
                
                if (df_valores_cidade['qtd_navios_porto'] > navios_max):
                    flag_outlier = 1
                elif (df_valores_cidade['qtd_navios_porto'] < navios_min):
                    flag_outlier = -1
                else:
                    flag_outlier = 0

                lista_valores = [cidade,
                                 qtd_dias,
                                 qtd_navios_porto_max,
                                 qtd_navios_porto_min,
                                 flag_outlier]

                lista_retorno.append(lista_valores)

        
        # estatísticas
        df_estatisticas = pd.DataFrame(lista_retorno, columns=['cidade',
                                                               'qtd_dias_consecutivos',
                                                               'qtd_navios_porto_max',
                                                               'qtd_navios_porto_min',
                                                               'flag_outlier'])
        
        # transforma dados em string
        df_estatisticas['qtd_dias_consecutivos'] = df_estatisticas['qtd_dias_consecutivos'].astype(str)
        df_estatisticas['qtd_navios_porto_max'] = df_estatisticas['qtd_navios_porto_max'].astype(str)
        df_estatisticas['qtd_navios_porto_min'] = df_estatisticas['qtd_navios_porto_min'].astype(str)
        df_estatisticas['flag_outlier'] = df_estatisticas['flag_outlier'].astype(str)
        
        return df_estatisticas
         
        
    def publica_conteudo(self):
        '''
        Publica previsão do tempo (tábua de marés)
        '''
        
        # data de hoje
        data_hoje = date.today().strftime("%d_%m_%Y")
        
        try:
            # gera resultados
            df_resultados = self.gera_df_navios()
            
            # salva resultados na pasta
            df_resultados[self.lista_colunas].to_csv(f"resultados_portos/{data_hoje}.csv", index=False, sep=';')
            
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
                status = df_linha['status']
                
                # salva foto
                if (status == '1'):
                    shutil.copy(f"imagens/img_satelite_{unidecode.unidecode(df_linha['cidade'])}.png", "foto.png")
                    time.sleep(3)

                # intent do conjunto de dados
                intent = self.atribui_intent(df_linha)
                if (intent == ""):
                    print ('intent vazio. tweet não pode ser publicado.')
                    continue

                # cria o tweet
                tweet = self.atribui_template(df_linha, intent)
                
                # emoji para aplicar
                elemento_random = random.choice([0, 1, 2, 3])
                if elemento_random == 0:
                    emoji = ''
                elif elemento_random == 1:
                    emoji = '[emoji_barco_1]'
                elif elemento_random == 2:
                    emoji = '[emoji_barco_2]'
                elif elemento_random == 3:
                    emoji = '[emoji_barco_3]'
                else:
                    continue
                    
                # aplica emoji
                tweet = tweet.replace(f"[emoji_barco]", emoji).strip()

                # verifica se pode publicar o tweet
                if (tweet == ""):
                    print ('tweet vazio. tweet não pode ser publicado.')
                    continue

                lista_atributos = ', '.join(df_linha.values.tolist())
                # verifica se tweet pode ser publicado                
                if (self.twitter_api.valida_tweet(tweet)):
                    try:
                        if (status == '1'):
                            self.twitter_api.make_tweet(tweet, self.modulo, intent, lista_atributos, 'foto')
                        else:
                            self.twitter_api.make_tweet(tweet, self.modulo, intent, lista_atributos, 'padrao')
                        
                        # espera um tempo para publicar novamente
                        print ('Tweet publicado')
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