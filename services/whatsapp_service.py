import requests
from config.settings import get_config

ACCESS_TOKEN = get_config("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = get_config("PHONE_NUMBER_ID")

BASE_URL = "https://graph.facebook.com/v19.0"


def enviar_template(numero: str, template: str, parametros=None):
    """
    Envia template aprovado pela Meta
    """
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("⚠️ Credenciais do WhatsApp não configuradas.")
        return

    url = f"{BASE_URL}/{PHONE_NUMBER_ID}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "template",
        "template": {
            "name": template,
            "language": {"code": "pt_BR"}
        }
    }

    # Caso tenha variáveis no template
    if parametros:
        payload["template"]["components"] = [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": p} for p in parametros
                ]
            }
        ]

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        print(f"✅ Template enviado para {numero}")

    except Exception as e:
        print(f"❌ Erro ao enviar template: {e}")