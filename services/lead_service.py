import os
import json
import pandas as pd
from datetime import datetime
from config.settings import USE_GOOGLE_SHEETS, SHEET_NAME
from config.settings import USE_GOOGLE_SHEETS, SHEET_NAME

# =========================
# GOOGLE SHEETS SETUP
# =========================
if USE_GOOGLE_SHEETS:
    import gspread
    import streamlit as st
    from google.oauth2.service_account import Credentials

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    def get_google_credentials():
        """
        Retorna credenciais do Google Sheets.
        1️⃣ Streamlit Secrets (produção)
        2️⃣ Variável de ambiente GOOGLE_CREDENTIALS (.env local)
        3️⃣ Arquivo JSON local (credenciais.json)
        """
        # Tenta usar Streamlit secrets
        try:
            creds_dict = st.secrets["GOOGLE_CREDENTIALS"]
            return Credentials.from_service_account_info(creds_dict, scopes=scope)
        except Exception:
            pass

        # Tenta usar .env
        credenciais_env = os.getenv("GOOGLE_CREDENTIALS")
        if credenciais_env:
            creds_dict = json.loads(credenciais_env)
            return Credentials.from_service_account_info(creds_dict, scopes=scope)

        # Fallback para arquivo local
        caminho = os.path.join(os.path.dirname(__file__), "..", "config", "credenciais.json")
        return Credentials.from_service_account_file(caminho, scopes=scope)

    creds = get_google_credentials()
    client = gspread.authorize(creds)

# =========================
# CARREGAR LEADS
# =========================
def carregar_leads():
    if USE_GOOGLE_SHEETS:
        sheet = client.open(SHEET_NAME).sheet1
        dados = sheet.get_all_values()

        if not dados:
            return pd.DataFrame(), sheet

        # remove linhas completamente vazias
        dados = [row for row in dados if any(cell.strip() for cell in row)]

        colunas = dados[0]
        linhas = dados[1:]
        df = pd.DataFrame(linhas, columns=colunas)

        return df, sheet
    else:
        df = pd.read_excel("data/leads.xlsx")
        return df

# =========================
# ATUALIZAR STATUS
# =========================
def atualizar_status(sheet_or_df, row, status):
    data_atual = datetime.now().strftime("%Y-%m-%d")

    if USE_GOOGLE_SHEETS:
        headers = sheet_or_df.row_values(1)
        try:
            col_status = headers.index("status") + 1
            col_data = headers.index("ultimo_envio") + 1
        except ValueError:
            print("❌ Colunas 'status' ou 'ultimo_envio' não encontradas")
            return

        sheet_or_df.update_cell(row, col_status, status)
        sheet_or_df.update_cell(row, col_data, data_atual)
    else:
        df = sheet_or_df
        df.at[row, "status"] = status
        df.at[row, "ultimo_envio"] = data_atual
        df.to_excel("data/leads.xlsx", index=False)

# =========================
# ATUALIZAR LINHA (DINÂMICO)
# =========================
def atualizar_linha(sheet, linha, dados):
    valores = ["" if pd.isna(v) else str(v) for v in dados.values()]
    ultima_coluna = chr(65 + len(valores) - 1)
    sheet.update(f"A{linha}:{ultima_coluna}{linha}", [valores])

# =========================
# REESCREVER PLANILHA COMPLETA
# =========================
def salvar_tudo(sheet, df):
    df = df.fillna("").astype(str)
    sheet.clear()
    sheet.append_row(df.columns.tolist())
    for _, row in df.iterrows():
        sheet.append_row(row.tolist())