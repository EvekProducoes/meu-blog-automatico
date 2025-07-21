import os
import requests
import google.generativeai as genai
import sys
from serpapi import GoogleSearch

# --- 1. CONFIGURAÇÃO E VALIDAÇÃO DAS CHAVES ---
try:
    GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
    FACEBOOK_PAGE_ID = os.environ['FACEBOOK_PAGE_ID']
    FACEBOOK_ACCESS_TOKEN = os.environ['FACEBOOK_ACCESS_TOKEN']
    SERPAPI_API_KEY = os.environ['SERPAPI_API_KEY']
except KeyError as e:
    print(f"ERRO: A chave secreta {e} não foi encontrada. Verifique as configurações do repositório.")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)


# --- 2. BUSCAR O PRINCIPAL TÓPICO (VERSÃO SERPAPI) ---
def get_top_trend():
    """Busca os tópicos em alta no Google para o Brasil usando SerpApi."""
    print("Buscando tópico em alta no Google via SerpApi...")
    try:
        params = {
          "engine": "google_trends",
          "data_type": "TRENDING_DAILY",
          "geo": "BR",
          "api_key": SERPAPI_API_KEY
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        
        daily_results = results.get("daily_results")
        
        if daily_results and daily_results[0].get("trending_searches"):
            first_trend = daily_results[0]["trending_searches"][0]
            if first_trend.get("title") and first_trend["title"].get("query"):
                top_trend = first_trend['title']['query']
                print(f"Tópico encontrado: {top_trend}")
                return top_trend
        
        print("Não foram encontrados tópicos em alta no SerpApi com a nova estrutura.")
        print("Resposta completa da API:", results)
        return None

    except Exception as e:
        print(f"ERRO ao buscar no SerpApi: {e}")
        return None

# --- 3. GERAR EXPLICAÇÃO COM O GEMINI ---
def generate_explanation_post(topic):
    """Gera um post para o Facebook explicando por que um tópico está em alta."""
