# config/settings.py
import os
import json

# =========================
# CONFIGURAÇÕES BÁSICAS
# =========================
EMAIL = os.getenv("EMAIL", "seuemail@exemplo.com")
SENHA = os.getenv("SENHA", "senha_do_email")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

INSTANCE_ID = os.getenv("INSTANCE_ID", "")
TOKEN = os.getenv("TOKEN", "")

try:
    DIAS_FOLLOWUP = int(os.getenv("DIAS_FOLLOWUP", 2))
except ValueError:
    DIAS_FOLLOWUP = 2

# =========================
# GOOGLE SHEETS
# =========================
USE_GOOGLE_SHEETS = str(os.getenv("USE_GOOGLE_SHEETS", "True")).strip().lower() in ["true", "1", "yes"]
SHEET_NAME = os.getenv("SHEET_NAME", "Leads Scalytech")

# Caminho para credenciais JSON local (não usa Streamlit Secrets)
GOOGLE_CRED_PATH = os.getenv("GOOGLE_CRED_PATH", "config/credenciais.json")

# =========================
# DEBUG / aviso
# =========================
if USE_GOOGLE_SHEETS and not os.path.exists(GOOGLE_CRED_PATH):
    print(f"⚠️ Arquivo de credenciais Google não encontrado em {GOOGLE_CRED_PATH}. Google Sheets não disponível.")