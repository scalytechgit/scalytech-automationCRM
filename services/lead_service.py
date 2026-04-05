# services/lead_service.py
import pandas as pd
from datetime import datetime
from config.settings import SHEET_NAME, get_google_creds
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# =========================
# GOOGLE SHEETS SETUP
# =========================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = get_google_creds()
if not creds_dict:
    raise RuntimeError("❌ Credenciais do Google não encontradas. Configure st.secrets['GOOGLE_CREDENTIALS'].")

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# =========================
# CARREGAR LEADS
# =========================
def carregar_leads():
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

# =========================
# ATUALIZAR STATUS
# =========================
def atualizar_status(sheet, row, status):
    data_atual = datetime.now().strftime("%Y-%m-%d")
    headers = sheet.row_values(1)

    try:
        col_status = headers.index("status") + 1
        col_data = headers.index("ultimo_envio") + 1
    except ValueError:
        raise RuntimeError("❌ Colunas 'status' ou 'ultimo_envio' não encontradas no Google Sheets")

    sheet.update_cell(row, col_status, status)
    sheet.update_cell(row, col_data, data_atual)

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