import datetime
import random
import json

class DiscourseOrderingClass:
    """
    Classe de ordenação do discurso
    """
    def __init__(self):
        # path json twitter
        path_frases_json = "frases_inicio_fim.json"
        f = open(path_frases_json, encoding='utf-8', mode="r")
        self.lista_frases = json.load(f)['frases']
        
        
    def adiciona_inicio_fim(self, frase):
        '''
        adiciona ao texto um início ou fim aleatoriamente selecionado
        '''
        valor = random.choice(self.lista_frases)
        
        # substitui bom dia, caso se aplique
        hora_atual = int(datetime.datetime.now().hour)
        
        # dia
        if hora_atual <= 11:
            valor = valor.replace("[Bom dia]", "Bom dia")
          
        # noite
        elif hora_atual >= 19:
            valor = valor.replace("[Bom dia]", "Boa noite")
          
        # tarde
        else:
            valor = valor.replace("[Bom dia]", "Boa tarde")
        
        # substitui valor
        if 'inicio' in valor:
            return valor.replace("[inicio]", "").replace("[fim]", "") + frase
        else:
            return frase + valor.replace("[inicio]", "").replace("[fim]", "")
        

    def discourse_ordering(self, intent, frase):
        '''
        aplica ordenação do discurso ao texto
        '''
        if "[permuta]" in frase:
            frase_0 = frase.split("[0]")[0]
            frase_1 = frase.split("[0]")[1].split("[1]")[0]
            frase_2 = frase.split("[1]")[1].split("[2]")[0]
            frase_3 = frase.split("[2]")[1]

            lista_frases = [frase_1, frase_2, frase_3]
            random.shuffle(lista_frases)

            frase_final = frase_0 + lista_frases[0] + ', a ' + lista_frases[1] + ' e a ' + lista_frases[2] + '.'
            frase_final = frase_final.replace('[permuta]', '').replace('[0]', '').replace('[1]', '').replace('[2]', '')
            return self.adiciona_inicio_fim(frase_final)
        else:
            return self.adiciona_inicio_fim(frase)