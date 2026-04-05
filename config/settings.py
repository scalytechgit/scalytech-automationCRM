import os

try:
    import streamlit as st
    USE_SECRETS = True
except ImportError:
    st = None
    USE_SECRETS = False

def get_config(key, default=None):
    """
    Retorna configuração:
    1️⃣ Streamlit secrets (produção)
    2️⃣ Variável de ambiente (.env local)
    3️⃣ Default se nada encontrado
    """
    # Prioridade: Streamlit Secrets
    if USE_SECRETS and st is not None:
        try:
            value = st.secrets.get(key)
            if value is not None:
                return value
        except Exception:
            pass

    # Fallback: variável de ambiente
    value = os.getenv(key)
    if value is not None:
        return value

    # Default
    return default

# =========================
# CONFIGURAÇÕES
# =========================

EMAIL = get_config("EMAIL", "seuemail@exemplo.com")
SENHA = get_config("SENHA", "senha_do_email")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

INSTANCE_ID = get_config("INSTANCE_ID", "")
TOKEN = get_config("TOKEN", "")

# Garante que DIAS_FOLLOWUP seja inteiro
try:
    DIAS_FOLLOWUP = int(get_config("DIAS_FOLLOWUP", 2))
except ValueError:
    DIAS_FOLLOWUP = 2

# Garante que USE_GOOGLE_SHEETS seja booleano
USE_GOOGLE_SHEETS = str(get_config("USE_GOOGLE_SHEETS", "True")).strip().lower() in ["true", "1", "yes"]

SHEET_NAME = get_config("SHEET_NAME", "Leads Scalytech")