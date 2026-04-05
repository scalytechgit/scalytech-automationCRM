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
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()  # Lança exceção se status != 2xx

        print(f"✅ WhatsApp enviado para {numero}")

    except requests.HTTPError:
        print(f"❌ Erro HTTP ao enviar WhatsApp ({response.status_code}): {response.text}")
    except requests.Timeout:
        print(f"❌ Timeout ao enviar WhatsApp para {numero}")
    except requests.ConnectionError:
        print(f"❌ Erro de conexão ao enviar WhatsApp para {numero}")
    except Exception as e:
        print(f"❌ Erro geral ao enviar WhatsApp para {numero}: {e}")