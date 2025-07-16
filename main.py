import os
import requests
import google.generativeai as genai
import sys
from urllib.parse import quote # Importação necessária para a nova função

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


# --- 2. BUSCAR TÓPICO (VERSÃO APRIMORADA) ---
def fetch_trending_topic():
    print("Tentativa 1: Buscando manchetes principais do Brasil...")
    url_headlines = f'https://gnews.io/api/v4/top-headlines?lang=pt&country=br&max=1&apikey={GNEWS_API_KEY}'
    try:
        response = requests.get(url_headlines)
        response.raise_for_status()
        articles = response.json().get('articles')
        if articles:
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
        if articles:
            topic = articles[0]['title']
            print(f"Tópico encontrado na segunda tentativa: {topic}")
            return topic
        else:
            print("Nenhum artigo encontrado em ambas as tentativas.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"ERRO na segunda tentativa de buscar notícias: {e}")
        return None

# --- 3. BUSCAR IMAGEM RELEVANTE (Pexels) ---
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
        else:
            print("Nenhuma imagem encontrada para o tópico.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao buscar imagem: {e}")
        return None

# --- 4. GERAR CONTEÚDO DO POST (Gemini AI) ---
def generate_facebook_post(topic):
    if not topic: return None
    print("Gerando texto do post com a API do Gemini...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Você é um social media especialista em criar posts para o Facebook para a página "NoticiandoDigital".
    Sua tarefa é criar um post curto e informativo sobre o seguinte tema, que é uma notícia relevante do dia no Brasil: "{topic}".
    O post deve seguir estas regras:
    - Ter um tom informativo, mas acessível e interessante.
    - Ter no máximo 3 parágrafos curtos.
    - Incluir 2 ou 3 emojis relevantes 📰🚀.
    - Terminar com 3 hashtags relevantes e populares.
    Responda apenas com o texto do post, sem qualquer outra introdução ou despedida.
    """
    try:
        response = model.generate_content(prompt)
        print("Texto gerado com sucesso.")
        return response.text
    except Exception as e:
        print(f"ERRO ao gerar conteúdo com o Gemini: {e}")
        return None

# --- 5. PUBLICAR NO FACEBOOK (VERSÃO FINAL COM UPLOAD DIRETO) ---
def post_to_facebook(message, image_url):
    if not message or not image_url:
        print("Conteúdo ou imagem faltando, publicação cancelada.")
        return
    
    # A mensagem agora precisa ser codificada para ir na URL
    message_encoded = quote(message)
    post_url = f'https://graph.facebook.com/{FACEBOOK_PAGE_ID}/photos?message={message_encoded}&access_token={FACEBOOK_ACCESS_TOKEN}'
    
    payload = {
        'url': image_url
    }
    
    try:
        print("Publicando no Facebook...")
        response = requests.post(post_url, data=payload)
        response.raise_for_status()
        print(">>> SUCESSO! Post publicado na Página do Facebook.")
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao postar no Facebook: {e}")
        print(f"Detalhes do erro: {e.response.json()}")

# --- FUNÇÃO PRINCIPAL ---
if __name__ == "__main__":
    print("--- INICIANDO ROTINA DE POSTAGEM AUTOMÁTICA ---")
    topic = fetch_trending_topic()
    if topic:
        # Para o teste final, vamos usar a imagem fixa para garantir.
        # Depois que funcionar, podemos trocar de volta para a busca dinâmica.
        # image_url = get_image_url(topic) 
        image_url = "https://images.pexels.com/photos/844297/pexels-photo-844297.jpeg" # Imagem de teste genérica
        print(f"Usando imagem de teste: {image_url}")
        
        post_text = generate_facebook_post(topic)
        post_to_facebook(post_text, image_url)
    else:
        print("Rotina encerrada pois não foi possível obter um tópico.")
    print("--- ROTINA FINALIZADA ---")
