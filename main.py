import os
import requests
import sys

# --- 1. CONFIGURAÇÃO E VALIDAÇÃO DAS CHAVES ---
try:
    FACEBOOK_PAGE_ID = os.environ['FACEBOOK_PAGE_ID']
    FACEBOOK_ACCESS_TOKEN = os.environ['FACEBOOK_ACCESS_TOKEN']
except KeyError as e:
    print(f"ERRO: A chave secreta {e} não foi encontrada. Verifique as configurações do repositório.")
    sys.exit(1)

# --- 2. PUBLICAR NO FACEBOOK (FUNÇÃO DE TESTE) ---
def post_to_facebook(message, image_url):
    if not message or not image_url:
        print("Conteúdo ou imagem faltando, publicação cancelada.")
        return
    
    post_url = f'https://graph.facebook.com/{FACEBOOK_PAGE_ID}/photos'
    
    params = {
        'url': image_url,
        'caption': message,
        'access_token': FACEBOOK_ACCESS_TOKEN
    }
    
    try:
        print("Publicando no Facebook (TESTE SIMPLIFICADO)...")
        response = requests.post(post_url, params=params)
        response.raise_for_status()
        print(">>> SUCESSO! Post publicado na Página do Facebook.")
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao postar no Facebook: {e}")
        if e.response:
            print(f"Detalhes do erro: {e.response.json()}")

# --- FUNÇÃO PRINCIPAL (LÓGICA DE TESTE FIXA) ---
if __name__ == "__main__":
    print("--- INICIANDO TESTE FINAL E SIMPLIFICADO ---")
    
    # Usando dados 100% fixos e simples
    test_message = "Este é um post de teste final com uma imagem simples para diagnóstico."
    test_image_url = "https://i.imgur.com/KzQ3oA8.png" # URL curta e limpa do Imgur

    print(f"Texto de teste: {test_message}")
    print(f"Imagem de teste: {test_image_url}")
    
    post_to_facebook(test_message, test_image_url)
    
    print("--- ROTINA FINALIZADA ---")
