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


# --- 2. BUSCAR O PRINCIPAL TÓPICO (VERSÃO SERPAPI CORRIGIDA) ---
def get_top_trend():
    """Busca os tópicos em alta no Google para o Brasil usando SerpApi."""
    print("Buscando tópico em alta no Google via SerpApi...")
    try:
        params = {
          "engine": "google_trends_trending_now",
          "frequency": "daily",
          "geo": "BR",
          "api_key": SERPAPI_API_KEY
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # AQUI ESTÁ A CORREÇÃO: O nome correto da lista é "daily_searches"
        trending_results = results.get("daily_searches")
        
        # A estrutura do título também é um pouco diferente
        if trending_results and trending_results[0].get("title"):
            top_trend = trending_results[0]['title']['query']
            print(f"Tópico encontrado: {top_trend}")
            return top_trend
        else:
            print("Não foram encontrados tópicos em alta no SerpApi. Verifique a resposta da API.")
            print("Resposta completa:", results) # Log extra para depuração
            return None
    except Exception as e:
        print(f"ERRO ao buscar no SerpApi: {e}")
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
    O tópico mais pesquisado no Brasil hoje é: "{topic}".
    Sua tarefa é escrever um post curto para o Facebook (2 ou 3 parágrafos) explicando o contexto e o motivo pelo qual as pessoas estão pesquisando sobre "{topic}".
    Seja direto, informativo e neutro.
    Termine o post com 3 hashtags relevantes, sendo a primeira a hashtag do próprio tópico.
    Responda apenas com o texto do post.
    """
    try:
        response = model.generate_content(prompt)
        print("Texto gerado com sucesso.")
        return response.text
    except Exception as e:
        print(f"ERRO ao gerar conteúdo com o Gemini: {e}")
        return None

# --- 4. PUBLICAR TEXTO NO FACEBOOK ---
def post_text_to_facebook(message):
    """Public
