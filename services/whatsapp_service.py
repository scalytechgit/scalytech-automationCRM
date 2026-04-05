import requests
from config.settings import INSTANCE_ID, TOKEN

def enviar_whatsapp(numero, mensagem):
    if not INSTANCE_ID or not TOKEN:
        print("⚠️ WhatsApp não enviado: INSTANCE_ID ou TOKEN não configurados")
        return

    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"

    payload = {
        "token": TOKEN,
        "to": numero,
        "body": mensagem
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print(f"✅ WhatsApp enviado para {numero}")
        else:
            print(f"❌ Erro WhatsApp ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"❌ Erro geral ao enviar WhatsApp para {numero}: {e}")