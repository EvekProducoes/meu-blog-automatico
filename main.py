import os
import requests
import google.generativeai as genai
import sys

# --- 1. CONFIGURAÇÃO E VALIDAÇÃO DAS CHAVES ---
try:
    GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
    NEWS_API_KEY = os.environ['NEWS_API_KEY']
    PEXELS_API_KEY = os.environ['PEXELS_API_KEY']
    FACEBOOK_PAGE_ID = os.environ['FACEBOOK_PAGE_ID']
    FACEBOOK_ACCESS_TOKEN = os.environ['FACEBOOK_ACCESS_TOKEN']
except KeyError as e:
    print(f"ERRO: A chave secreta {e} não foi encontrada. Verifique as configurações do repositório.")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# --- 2. BUSCAR TÓPICO EM ALTA ---
def fetch_trending_topic():
    print("Buscando tópico em alta no NewsAPI.org...")
    url = f'https://newsapi.org/v2/top-headlines?country=br&apiKey={NEWS_API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get('articles')
        if articles:
            topic = articles[0]['title']
            print(f"Tópico encontrado: {topic}")
            return topic
        else:
            print("Nenhum artigo encontrado.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao buscar notícias: {e}")
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
        else:
            print("Nenhuma imagem encontrada para o tópico.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao buscar imagem: {e}")
        return None

# --- 4. GERAR CONTEÚDO DO POST ---
def generate_facebook_post(topic):
    if not topic: return None
    print("Gerando texto do post com a API do Gemini...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Você é um social media especialista em criar posts para o Facebook para a página "NoticiandoDigital".
    Sua tarefa é criar um post curto e informativo sobre o seguinte tema, que é a manchete do dia no Brasil: "{topic}".
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

# --- 5. PUBLICAR NO FACEBOOK ---
def post_to_facebook(message, image_url):
    if not message or not image_url:
        print("Conteúdo ou imagem faltando, publicação cancelada.")
        return
    print("Publicando no Facebook...")
    post_url = f'https://graph.facebook.com/{FACEBOOK_PAGE_ID}/photos'
    payload = {
        'message': message,
        'url': image_url,
        'access_token': FACEBOOK_ACCESS_TOKEN
    }
    try:
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
        image_url = get_image_url(topic)
        post_text = generate_facebook_post(topic)
        post_to_facebook(post_text, image_url)
    else:
        print("Rotina encerrada pois não foi possível obter um tópico.")
    print("--- ROTINA FINALIZADA ---")
