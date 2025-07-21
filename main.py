import os
import requests
import google.generativeai as genai
import sys
from pytrends.request import TrendReq

# --- 1. CONFIGURAÇÃO E VALIDAÇÃO DAS CHAVES ---
# Agora só precisamos de 3 chaves!
try:
    GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
    FACEBOOK_PAGE_ID = os.environ['FACEBOOK_PAGE_ID']
    FACEBOOK_ACCESS_TOKEN = os.environ['FACEBOOK_ACCESS_TOKEN']
except KeyError as e:
    print(f"ERRO: A chave secreta {e} não foi encontrada. Verifique as configurações do repositório.")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)


# --- 2. BUSCAR O PRINCIPAL TÓPICO DO GOOGLE TRENDS ---
def get_top_trend():
    """Busca o tópico número 1 em alta no Google Trends para o Brasil."""
    print("Buscando tópico em alta no Google Trends Brasil...")
    try:
        pytrends = TrendReq(hl='pt-BR', tz=360)
        trending_df = pytrends.trending_searches(pn='brazil')
        if not trending_df.empty:
            top_trend = trending_df.iloc[0, 0]
            print(f"Tópico encontrado: {top_trend}")
            return top_trend
        else:
            print("Não foram encontrados tópicos em alta no Google Trends.")
            return None
    except Exception as e:
        print(f"ERRO ao buscar no Google Trends: {e}")
        return None

# --- 3. GERAR EXPLICAÇÃO COM O GEMINI ---
def generate_explanation_post(topic):
    """Gera um post para o Facebook explicando por que um tópico está em alta."""
    if not topic:
        return None
    
    print(f"Gerando explicação para '{topic}' com a API do Gemini...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Você é um redator para a página "NoticiandoDigital". Sua especialidade é explicar de forma clara e concisa por que um determinado assunto está em alta nas buscas.
    O tópico mais pesquisado no
