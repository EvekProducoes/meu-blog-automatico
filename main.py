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
    """Busca os tópicos em alta no Google para o Brasil usando o novo endpoint do SerpApi."""
    print("Buscando tópico em alta no Google via SerpApi (usando novo endpoint)...")
    try:
        params = {
          "engine": "google_trends",
          "data_type": "TRENDING_DAILY", # Novo parâmetro exigido
          "geo": "BR",
          "api_key": SERPAPI_API_KEY
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # A nova estrutura da resposta é diferente
        daily_results = results.get("daily_results")
        
        if daily_results and daily_results[0].get("trending_searches"):
            first_trend = daily_results[0]["trending_searches"][0]
            if first_trend.get("title") and first_trend["title"].get("query"):
                top_trend = first_trend['title']['query']
                print(f"Tópico encontrado: {top_trend}")
                return top_trend
        
        print("Não foram encontrados tópicos em alta no SerpApi com a nova estrutura.")
        print("Resposta completa da API:", results) # Log extra para depuração
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
    """Publica um post de texto no feed da Página do Facebook."""
    if not message:
        print("Conteúdo faltando, publicação cancelada.")
        return
    
    post_url = f'https://graph.facebook.com/{FACEBOOK_PAGE_ID}/feed'
    
    payload = {
        'message': message,
        'access_token': FACEBOOK_ACCESS_TOKEN
    }
    
    try:
        print("Publicando no Facebook (usando o endpoint /feed)...")
        response = requests.post(post_url, data=payload)
        response.raise_for_status()
        print(">>> SUCESSO! Post de texto publicado na Página do Facebook.")
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao postar no Facebook: {e}")
        if e.response:
            print(f"Detalhes do erro: {e.response.json()}")

# --- FUNÇÃO PRINCIPAL ---
if __name__ == "__main__":
    print("---
