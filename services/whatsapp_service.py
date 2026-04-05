# services/whatsapp_service.py
import requests
from config.settings import INSTANCE_ID, TOKEN

def enviar_whatsapp(numero: str, mensagem: str):
    """
    Envia mensagem via WhatsApp usando API UltraMsg.
    Funciona local ou no Streamlit Cloud.
    """
    if not INSTANCE_ID or not TOKEN:
        print("⚠️ WhatsApp não enviado: INSTANCE_ID ou TOKEN não configurados.")
        return

    if not numero or not mensagem:
        print("⚠️ Número ou mensagem vazios. WhatsApp não enviado.")
        return

    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"
    payload = {
        "token": TOKEN,
        "to": numero,
        "body": mensagem
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            print(f"✅ WhatsApp enviado para {numero}")
        else:
            print(f"❌ Erro WhatsApp ({response.status_code}): {response.text}")
    except requests.Timeout:
        print(f"❌ Timeout ao enviar WhatsApp para {numero}")
    except requests.ConnectionError:
        print(f"❌ Erro de conexão ao enviar WhatsApp para {numero}")
    except Exception as e:
        print(f"❌ Erro geral ao enviar WhatsApp para {numero}: {e}")