import pandas as pd
from datetime import datetime
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

    creds = Credentials.from_service_account_info(
        st.secrets["GOOGLE_CREDENTIALS"],
        scopes=scope
    )

    client = gspread.authorize(creds)


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
        # pega cabeçalho
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
    valores = []

    for v in dados.values():
        if pd.isna(v):
            valores.append("")
        else:
            valores.append(str(v))

    # calcula última coluna dinamicamente (A, B, C...)
    ultima_coluna = chr(65 + len(valores) - 1)

    sheet.update(f"A{linha}:{ultima_coluna}{linha}", [valores])


# =========================
# REESCREVER PLANILHA (IMPORTANTE)
# =========================
def salvar_tudo(sheet, df):
    df = df.fillna("").astype(str)

    # limpa tudo
    sheet.clear()

    # escreve cabeçalho
    sheet.append_row(df.columns.tolist())

    # escreve dados
    for _, row in df.iterrows():
        sheet.append_row(row.tolist())