import requests
from config.settings import INSTANCE_ID, TOKEN
from config.settings import USE_GOOGLE_SHEETS, SHEET_NAME

def enviar_whatsapp(numero, mensagem):
    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"

    payload = {
        "token": TOKEN,
        "to": numero,
        "body": mensagem
    }

    try:
        response = requests.post(url, data=payload)

        if response.status_code == 200:
            print(f"WhatsApp enviado para {numero}")
        else:
            print("Erro WhatsApp:", response.text)

    except Exception as e:
        print("Erro geral:", e)