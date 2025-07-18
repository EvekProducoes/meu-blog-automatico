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


# --- 2. BUSCAR TÓPICO (VERSÃO REFINADA COM CATEGORIA) ---
def fetch_trending_topic():
    """Busca a principal manchete da categoria 'tecnologia' no Brasil."""
    print("Buscando manchete de TECNOLOGIA no Brasil...")
    
    category = "technology"
    url = f'https://gnews.io/api/v4/top-headlines?category={category}&lang=pt&country=br&max=1&apikey={GNEWS_API_KEY}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get('articles')
        if articles and articles[0].get('title'):
            topic = articles[0]['title']
            print(f"Tópico de tecnologia encontrado: {topic}")
            return topic
        else:
            print(f"Nenhum artigo de '{category}' encontrado hoje.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao buscar notícias de tecnologia: {e}")
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
    return "https://images.pexels.com/photos/3861958/pexels-photo-3861958.jpeg"

# --- 4. GERAR CONTEÚDO DO POST ---
def generate_facebook_post(topic):
    if not topic: return None
    print("Gerando texto do post com a API do Gemini...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Você é um social media especialista em criar posts para o Facebook para a página "NoticiandoDigital", focada em tecnologia e inovação.
    Sua tarefa é criar um post curto e informativo sobre a seguinte manchete de tecnologia do dia no Brasil: "{topic}".
    O post deve ter um tom informativo, mas acessível e interessante. Inclua 2 ou 3 emojis relevantes 💻🚀.
    Termine com 3 hashtags relevantes como #Tecnologia #Inovação e uma terceira relacionada ao tópico.
    Responda apenas com o texto do post.
    """
    try:
        response = model.generate_content(prompt)
        print("Texto gerado com sucesso.")
        return response.text
    except Exception as e:
        print(f"ERRO ao gerar conteúdo com o Gemini: {e}")
        return None

# --- 5. PUBLICAR NO FACEBOOK (VERSÃO 100% CORRIGIDA) ---
def post_to_facebook(message, image_url):
    if not message or not image_url:
        print("Conteúdo ou imagem faltando, publicação cancelada.")
        return
    
    post_url = f'https://graph.facebook.com/{FACEBOOK_PAGE_ID}/photos'
    
    # A mensagem, a url da imagem e o token vão todos juntos no payload
    payload = {
        'url': image_url,
        'message': message,
        'access_token': FACEBOOK_ACCESS_TOKEN
    }
    
    try:
        print("Publicando no Facebook...")
        response = requests.post(post_url, data=payload)
        response.raise_for_status()
        print(">>> SUCESSO! Post publicado na Página do Facebook.")
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao postar no Facebook: {e}")
        if e.response:
            print(f"Detalhes do erro: {e.response.json()}")

# --- FUNÇÃO PRINCIPAL ---
if __name__ == "__main__":
    print("--- INICIANDO ROTINA DE POSTAGEM AUTOMÁTICA ---")
    topic = fetch_trending_topic()
    
    if topic:
        post_text = generate_facebook_post(topic)
        image_url = get_image_url(topic)
        
        if post_text and image_url:
            post_to_facebook(post_text, image_url)
        else:
            print("Falha na geração do post ou busca da imagem. Publicação cancelada.")
    else:
        print("Rotina encerrada pois não foi possível obter um tópico de tecnologia hoje.")
    
    print("--- ROTINA FINALIZADA ---")
