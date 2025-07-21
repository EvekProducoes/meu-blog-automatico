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
    print("--- INICIANDO ROTINA DO EXPLICADOR DE TENDÊNCIAS ---")
    topic = get_top_trend()
    
    if topic:
        post_text = generate_explanation_post(topic)
        if post_text:
            post_text_to_facebook(post_text)
        else:
            print("Não foi possível gerar a explicação para o tópico.")
    else:
        print("Rotina encerrada pois não foi possível obter um tópico do Google Trends.")
    
    print("--- ROTINA FINALIZADA ---")
