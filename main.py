import requests
import urllib.parse

def post_to_facebook(page_id, access_token, caption, image_url):
    url = f"https://graph.facebook.com/{page_id}/photos"
    # Codificar a legenda e a URL da imagem
    encoded_caption = urllib.parse.quote(caption)
    encoded_image_url = urllib.parse.quote(image_url)
    
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

# Exemplo de uso
page_id = "SEU_PAGE_ID"
access_token = "SEU_ACCESS_TOKEN"
caption = "🚨 Garanta já seu produto Apple com mega desconto! 🚨 A Amazon dos EUA está com ofertas imperdíveis, com descontos de até 32% em diversos produtos! 💻🚀 Corra para garantir o seu antes que acabe! Link na bio. 😉 #Tecnologia #Inovação #AppleDescontos"
image_url = "https://images.pexels.com/photos/30366457/pexels-photo-30366457.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"

post_to_facebook(page_id, access_token, caption, image_url)
