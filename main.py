import requests
import os

def post_to_facebook(page_id, access_token, caption, image_url):
    url = f"https://graph.facebook.com/{page_id}/photos"
    payload = {
        "url": image_url,
        "caption": caption,
        "access_token": access_token
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Postagem realizada com sucesso!")
        else:
            print(f"Erro ao postar: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro na solicitação: {str(e)}")

# Carregar variáveis do ambiente ou interface
access_token = os.getenv("FB_ACCESS_TOKEN")  # Ajuste o nome conforme GitHub
page_id = os.getenv("PAGE_ID")  # Ajuste o nome conforme GitHub
caption = "🚨 Garanta já seu produto Apple com mega desconto! 🚨 A Amazon dos EUA está com ofertas imperdíveis, com descontos de até 32% em diversos produtos! 💻🚀 Corra para garantir o seu antes que acabe! Link na bio. 😉 #Tecnologia #Inovação #AppleDescontos"
image_url = "https://images.pexels.com/photos/30366457/pexels-photo-30366457.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"

post_to_facebook(page_id, access_token, caption, image_url)
