# services/lead_service.py
import pandas as pd
from datetime import datetime
from config.settings import USE_GOOGLE_SHEETS, SHEET_NAME, GOOGLE_CRED_PATH

client = None  # inicializa client

# =========================
# GOOGLE SHEETS SETUP
# =========================
if USE_GOOGLE_SHEETS:
    try:
        import gspread
    except ImportError:
        raise RuntimeError("gspread não instalado. Rode: pip install gspread")

    from oauth2client.service_account import ServiceAccountCredentials

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    # Inicializa client usando o arquivo credenciais.json
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CRED_PATH, SCOPES)
        client = gspread.authorize(creds)
    except Exception as e:
        client = None
        print(f"⚠️ Erro ao autenticar Google Sheets: {e}")
        print("Google Sheets não disponível.")


# =========================
# CARREGAR LEADS
# =========================
def carregar_leads():
    if USE_GOOGLE_SHEETS and client:
        sheet = client.open(SHEET_NAME).sheet1
        dados = sheet.get_all_values()

        # Cabeçalho padrão se planilha vazia
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
        raise RuntimeError("Google Sheets não disponível. Verifique credenciais ou arquivo config/credenciais.json.")


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
# ATUALIZAR LINHA DINÂMICA
# =========================
def atualizar_linha(sheet, linha, dados):
    if USE_GOOGLE_SHEETS and client:
        valores = ["" if pd.isna(v) else str(v) for v in dados.values()]
        # Atualiza da coluna A até a última coluna necessária
        ultima_coluna = chr(64 + len(valores))  # 65 = A
        sheet.update(f"A{linha}:{ultima_coluna}{linha}", [valores])


# =========================
# SALVAR PLANILHA COMPLETA
# =========================
def salvar_tudo(sheet, df):
    if USE_GOOGLE_SHEETS and client:
        df = df.fillna("").astype(str)
        sheet.clear()
        # Escreve cabeçalho
        sheet.append_row(df.columns.tolist())
        # Escreve cada linha
        for _, row in df.iterrows():
            sheet.append_row(row.tolist())