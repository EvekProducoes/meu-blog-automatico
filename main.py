import os
import requests
import sys

def post_to_facebook(page_id, access_token, caption, image_url):
    """
    Faz uma postagem no Facebook usando a Graph API.
    Usa o endpoint /feed para postar mensagem e link da imagem.
    """
    post_url = f"https://graph.facebook.com/{page_id}/feed"
    
    payload = {
        'message': caption,
        'link': image_url,
        'access_token': access_token
    }
    
    try:
        print("Publicando no Facebook (usando o endpoint /feed)...")
        response = requests.post(post_url, data=payload)
        response.raise_for_status() # Lança um erro se a resposta não for 2xx
        print(">>> SUCESSO! Post publicado na Página do Facebook.")
        print(f"Detalhes da resposta: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao postar no Facebook: {e}")
        if e.response:
            print(f"Detalhes do erro: {e.response.json()}")

def main():
    """
    Função principal que executa a rotina de postagem de teste.
    """
    print("--- INICIANDO ROTINA DE POSTAGEM DE TESTE (/feed) ---")
    
    # Carrega as variáveis de ambiente com os nomes corretos do GitHub Secrets
    access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    
    # Verifica se as variáveis foram carregadas
    if not page_id or not access_token:
        print("ERRO: FACEBOOK_PAGE_ID ou FACEBOOK_ACCESS_TOKEN não configurados. Verifique os segredos do repositório.")
        print("--- ROTINA FINALIZADA ---")
        return
        
    print("Variáveis de ambiente carregadas com sucesso.")

    # Configurações da postagem de teste
    caption = "🚨 Teste de Publicação! 🚨 Usando o endpoint /feed para postar uma mensagem com um link de imagem. Se você está vendo isso, o método alternativo funcionou! 😉 #Teste #API #FacebookDev"
    image_url = "https://i.imgur.com/KzQ3oA8.png" # Usando uma URL de imagem simples e confiável
    
    print(f"Texto do post: {caption}")
    print(f"Link da imagem: {image_url}")
    
    post_to_facebook(page_id, access_token, caption, image_url)
    
    print("--- ROTINA FINALIZADA ---")

if __name__ == "__main__":
    main()
