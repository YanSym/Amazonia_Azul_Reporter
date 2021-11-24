# Imports
from metodos_auxiliares_news import HelperClassNews

# classe auxiliar
helper_class = HelperClassNews()

# pesquisa notícias
df_news = helper_class.pesquisa_news()
      
# seleciona e posta tweet mais relevante
helper_class.posta_tweet_noticia(df_news)