import os
import requests
import google.generativeai as genai
import sys
from urllib.parse import quote

# --- 1. CONFIGURAÇÃO E VALIDAÇÃO DAS CHAVES ---
try:
    GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
    GNEWS_API_KEY = os.environ['GNEWS_API_KEY']
    PEXELS_API_KEY = os.environ['PEXELS_API_KEY']
    FACEBOOK_PAGE_ID = os.environ['FACEBOOK_PAGE_ID']
    FACEBOOK_ACCESS_TOKEN = os.environ['FACEBOOK_ACCESS_TOKEN']
except KeyError as e:
    print(f"ERRO: A chave secreta {e} não foi encontrada. Verifique as configurações do repositório.")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# --- 2. BUSCAR TÓPICO ---
def fetch_trending_topic():
    print("Tentativa 1: Buscando manchetes principais do Brasil...")
    url_headlines = f'https://gnews.io/api/v4/top-headlines?lang=pt&country=br&max=1&apikey={GNEWS_API_KEY}'
    try:
        response = requests.get(url_headlines)
        response.raise_for_status()
        articles = response.json().get('articles')
        if articles and articles[0].get('title'):
            topic = articles[0]['title']
            print(f"Tópico encontrado na primeira tentativa: {topic}")
            return topic
    except requests.exceptions.RequestException as e:
        print(f"ERRO na primeira tentativa de buscar notícias: {e}")

    print("Primeira tentativa não retornou resultados. Tentando busca genérica por 'Brasil'...")
    url_search = f'https://gnews.io/api/v4/search?q=Brasil&lang=pt&country=br&max=1&apikey={GNEWS_API_KEY}'
    try:
        response = requests.get(url_search)
        response.raise_for_status()
        articles = response.json().get('articles')
        if articles and articles[0].get('title'):
            topic = articles[0]['title']
            print(f"Tópico encontrado na segunda tentativa: {topic}")
            return topic
    except requests.exceptions.RequestException as e:
        print(f"ERRO na segunda tentativa de buscar notícias: {e}")
    
    print("Nenhum artigo encontrado em ambas as tentativas.")
    return None

# --- 3. BUSCAR IMAGEM RELEVANTE ---
def get_image_url(query):
    if not query: return None
    print(f"Buscando imagem para '{query}' no Pexels...")
    url = f'https://api.pexels.com/v1/search?query={query}&per_page=1&orientation=landscape'
    headers = {'Authorization': PEXELS_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        photos = response.json().get('photos')
        if photos:
            image_url = photos[0]['src']['large']
            print(f"Imagem encontrada: {image_url}")
            return image_url
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao buscar imagem: {e}")
    
    print("Nenhuma imagem encontrada para o tópico. Usando imagem de contingência.")
    return "https://images.pexels.com/photos/2882552/pexels-photo-2882552.jpeg"

# --- 4. GERAR CONTEÚDO DO POST ---
def generate_facebook_post(topic):
    if not topic: return None
    print("Gerando texto do post com a API do Gemini...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Você é um social media especialista em criar posts para o Facebook para a página "NoticiandoDigital".
    Sua tarefa é criar um post curto e informativo sobre o seguinte tema, que é uma notícia relevante do dia no Brasil: "{topic}".
    O post deve ter um tom informativo, mas acessível. Inclua 2 ou 3 emojis e 3 hashtags relevantes.
    Responda apenas com o texto do post.
    """
    try:
        response = model.generate_content(prompt)
        print("Texto gerado com sucesso.")
        return response.text
    except Exception as e:
        print(f"ERRO ao gerar conteúdo com o Gemini: {e}")
        return None

# --- 5. PUBLICAR NO FACEBOOK (VERSÃO CORRIGIDA COM UPLOAD DIRETO) ---
def post_to_facebook(message, image_url):
    if not message or not image_url:
        print("Conteúdo ou imagem faltando, publicação cancelada.")
        return
    
    message_encoded = quote(message)
    post_url = f'https://graph.facebook.com/{FACEBOOK_PAGE_ID}/feed'
    payload = {
        'message': message_encoded,
        'url': image_url,
        'access_token': FACEBOOK_ACCESS_TOKEN
    }
    
    print(f"URL: {post_url}")
    print(f"Payload: {payload}")
    
    try:
        print("Publicando no Facebook...")
        response = requests.post(post_url, data=payload)
        response.raise_for_status()
        print(">>> SUCESSO! Post publicado na Página do Facebook.")
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao postar no Facebook: {e}")
        if e.response:
            print(f"Detalhes do erro: {e.response.json()}")

# --- FUNÇÃO PRINCIPAL (LÓGICA DE CONTINGÊNCIA) ---
if __name__ == "__main__":
    print("--- INICIANDO ROTINA DE POSTAGEM AUTOMÁTICA ---")
    topic = fetch_trending_topic()
    
    if not topic:
        print("Nenhum tópico de notícia encontrado. Gerando um post de contingência.")
        topic = "Resumo de Notícias" 
        post_text = "Fique por dentro das últimas novidades e acontecimentos. O NoticiandoDigital traz para você as informações mais recentes! 🌐 #Notícias #Brasil #Atualidades"
        image_url = get_image_url(topic) 
    else:
        post_text = generate_facebook_post(topic)
        image_url = get_image_url(topic)

    if post_text and image_url:
        post_to_facebook(post_text, image_url)
    else:
        print("Falha na geração do post ou busca da imagem. Publicação cancelada.")
    
    print("--- ROTINA FINALIZADA ---")
