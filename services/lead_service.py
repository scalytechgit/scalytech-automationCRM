import os
import json
import pandas as pd
from datetime import datetime
from config.settings import USE_GOOGLE_SHEETS, SHEET_NAME

# =========================
# GOOGLE SHEETS SETUP
# =========================
client = None  # inicializa client

if USE_GOOGLE_SHEETS:
    import gspread
    try:
        import streamlit as st
    except ImportError:
        st = None  # fallback local sem Streamlit

    from google.oauth2.service_account import Credentials

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    def get_google_credentials():
        """Retorna credenciais do Google Sheets ou None se não houver."""
        creds = None

        # 1️⃣ Streamlit secrets
        if st:
            try:
                creds = st.secrets.get("GOOGLE_CREDENTIALS")
                if creds:
                    # Pode ser AttrDict ou string JSON
                    if isinstance(creds, str):
                        creds = json.loads(creds)
                    elif hasattr(creds, "_to_dict"):  # AttrDict
                        creds = dict(creds)
            except Exception:
                pass

        # 2️⃣ Variável de ambiente
        if creds is None:
            env_creds = os.getenv("GOOGLE_CREDENTIALS")
            if env_creds:
                try:
                    creds = json.loads(env_creds)
                except Exception:
                    pass

        # 3️⃣ Arquivo local
        if creds is None:
            local_path = os.path.join(os.path.dirname(__file__), "..", "config", "credenciais.json")
            if os.path.isfile(local_path):
                creds = local_path  # será usado como arquivo

        if creds is None:
            print("⚠️ Nenhuma credencial Google encontrada. Google Sheets não disponível.")
            return None

        # ✅ Corrige o erro do AttrDict
        if isinstance(creds, dict):
            return Credentials.from_service_account_info(creds, scopes=SCOPES)
        else:  # string caminho do arquivo
            return Credentials.from_service_account_file(creds, scopes=SCOPES)

    creds = get_google_credentials()
    if creds:
        client = gspread.authorize(creds)
    else:
        client = None  # evita que quebre

# =========================
# CARREGAR LEADS
# =========================
def carregar_leads():
    if USE_GOOGLE_SHEETS and client:
        sheet = client.open(SHEET_NAME).sheet1
        dados = sheet.get_all_values()

        if not dados:
            colunas = ["cliente","nicho","email","instagram","site","telefone","status","ultimo_envio"]
            return pd.DataFrame(columns=colunas), sheet

        # remove linhas vazias
        dados = [row for row in dados if any(cell.strip() for cell in row)]
        colunas = dados[0]
        linhas = dados[1:]
        df = pd.DataFrame(linhas, columns=colunas)
        return df, sheet
    else:
        raise RuntimeError(
            "Google Sheets não disponível. Configure credenciais via Streamlit secrets, variável de ambiente ou arquivo local."
        )

# =========================
# ATUALIZAR STATUS
# =========================
def atualizar_status(sheet, row, status):
    data_atual = datetime.now().strftime("%Y-%m-%d")
    if USE_GOOGLE_SHEETS and client:
        headers = sheet.row_values(1)
        col_status = headers.index("status") + 1
        col_data = headers.index("ultimo_envio") + 1
        sheet.update_cell(row, col_status, status)
        sheet.update_cell(row, col_data, data_atual)

# =========================
# ATUALIZAR LINHA
# =========================
def atualizar_linha(sheet, linha, dados):
    if USE_GOOGLE_SHEETS and client:
        valores = ["" if pd.isna(v) else str(v) for v in dados.values()]
        ultima_coluna = chr(65 + len(valores) - 1)
        sheet.update(f"A{linha}:{ultima_coluna}{linha}", [valores])

# =========================
# SALVAR PLANILHA COMPLETA
# =========================
def salvar_tudo(sheet, df):
    if USE_GOOGLE_SHEETS and client:
        df = df.fillna("").astype(str)
        sheet.clear()
        sheet.append_row(df.columns.tolist())
        for _, row in df.iterrows():
            sheet.append_row(row.tolist())