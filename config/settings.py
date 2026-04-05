import os
import json

# =========================
# STREAMLIT SECRETS DETECTION
# =========================
try:
    import streamlit as st
    USE_SECRETS = True
except ImportError:
    USE_SECRETS = False

# =========================
# GET CONFIG
# =========================
def get_config(key, default=None):
    """
    Pega valor do Streamlit secrets (deploy) ou variável de ambiente local.
    """
    if USE_SECRETS:
        value = st.secrets.get(key)
        if value is not None:
            return value
    return os.getenv(key, default)

# =========================
# CONFIGURAÇÕES PRINCIPAIS
# =========================
EMAIL = get_config("EMAIL")
SENHA = get_config("SENHA")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

INSTANCE_ID = get_config("INSTANCE_ID")
TOKEN = get_config("TOKEN")

# Dias de follow-up
try:
    DIAS_FOLLOWUP = int(get_config("DIAS_FOLLOWUP", 2))
except ValueError:
    DIAS_FOLLOWUP = 2

# Converte string para bool
def str_to_bool(s):
    return str(s).lower() in ["true", "1", "yes"]

USE_GOOGLE_SHEETS = str_to_bool(get_config("USE_GOOGLE_SHEETS", "true"))
SHEET_NAME = get_config("SHEET_NAME", "Leads Scalytech")

# =========================
# GOOGLE CREDENTIALS
# =========================
def get_google_creds():
    """
    Retorna credenciais do Google como dicionário.
    Usa st.secrets no Cloud ou lê localmente config/credentials.json
    """
    if not USE_GOOGLE_SHEETS:
        return None

    if USE_SECRETS:
        creds_str = st.secrets.get("GOOGLE_CREDENTIALS")
        if creds_str:
            return json.loads(creds_str)
        else:
            raise RuntimeError("❌ GOOGLE_CREDENTIALS não encontrado no secrets.toml")
    else:
        cred_path = "config/credentials.json"
        if os.path.exists(cred_path):
            with open(cred_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"❌ Arquivo {cred_path} não encontrado")