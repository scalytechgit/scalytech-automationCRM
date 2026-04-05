from services.lead_service import carregar_leads, atualizar_status
from services.email_service import enviar_email
from services.whatsapp_service import enviar_whatsapp
from config.settings import DIAS_FOLLOWUP, USE_GOOGLE_SHEETS

from datetime import datetime
from config.settings import USE_GOOGLE_SHEETS, SHEET_NAME
import pandas as pd
import os


# =========================
# TEMPLATE
# =========================
def carregar_template(nome_arquivo):
    base_path = os.path.dirname(os.path.abspath(__file__))
    caminho = os.path.join(base_path, "..", "templates", nome_arquivo)

    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()


def processar_email(template, cliente, assunto_padrao):
    mensagem = template.replace("{cliente}", cliente)

    if "\n" in mensagem:
        assunto, corpo = mensagem.split("\n", 1)
        assunto = assunto.replace("Assunto: ", "").strip()
    else:
        assunto = assunto_padrao
        corpo = mensagem

    return assunto, corpo


# =========================
# PROCESSAMENTO
# =========================
def processar_leads():
    data = carregar_leads()

    if isinstance(data, tuple):
        df, sheet = data
    else:
        df = data
        sheet = None

    df = pd.DataFrame(df)

    if df.empty:
        print("⚠️ Nenhum lead encontrado")
        return

    for i, row in df.iterrows():
        linha_sheet = i + 2

        cliente = str(row.get("cliente", "")).strip()
        email = str(row.get("email", "")).strip()
        telefone = str(row.get("telefone", "")).strip()
        status = str(row.get("status", "")).lower().strip()
        ultimo_envio = row.get("ultimo_envio")

        # =========================
        # VALIDAÇÃO
        # =========================
        if not cliente or not email:
            continue

        if status == "respondido":
            continue

        # =========================
        # NOVO LEAD
        # =========================
        if status == "novo":
            try:
                # EMAIL
                template_email = carregar_template("email_1.txt")
                assunto, corpo = processar_email(
                    template_email,
                    cliente,
                    "Contato Scalytech"
                )

                enviar_email(email, assunto, corpo)

                # WHATSAPP
                if telefone:
                    template_wpp = carregar_template("whatsapp_1.txt")
                    mensagem_wpp = template_wpp.replace("{cliente}", cliente)

                    enviar_whatsapp(telefone, mensagem_wpp)

                atualizar_status(
                    sheet if USE_GOOGLE_SHEETS else df,
                    linha_sheet,
                    "enviado"
                )

                print(f"✅ Lead novo processado: {cliente}")

            except Exception as e:
                print(f"❌ Erro ao enviar para {cliente}: {e}")

        # =========================
        # FOLLOW-UP
        # =========================
        elif (
            status == "enviado"
            and pd.notna(ultimo_envio)
            and str(ultimo_envio).strip() != ""
        ):
            try:
                data_envio = pd.to_datetime(ultimo_envio)
                dias = (datetime.now() - data_envio).days
            except:
                continue

            if dias >= DIAS_FOLLOWUP:
                try:
                    # EMAIL
                    template_email = carregar_template("email_followup.txt")
                    assunto, corpo = processar_email(
                        template_email,
                        cliente,
                        "Follow-up Scalytech"
                    )

                    enviar_email(email, assunto, corpo)

                    # WHATSAPP
                    if telefone:
                        template_wpp = carregar_template("whatsapp_followup.txt")
                        mensagem_wpp = template_wpp.replace("{cliente}", cliente)

                        enviar_whatsapp(telefone, mensagem_wpp)

                    atualizar_status(
                        sheet if USE_GOOGLE_SHEETS else df,
                        linha_sheet,
                        "followup"
                    )

                    print(f"🔁 Follow-up enviado: {cliente}")

                except Exception as e:
                    print(f"❌ Erro no follow-up para {cliente}: {e}")

        # =========================
        # IGNORA
        # =========================
        elif status == "followup":
            continue