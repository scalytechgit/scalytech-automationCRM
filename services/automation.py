from services.lead_service import carregar_leads, atualizar_status
from services.email_service import enviar_email
from services.whatsapp_service import enviar_whatsapp
from config.settings import DIAS_FOLLOWUP, USE_GOOGLE_SHEETS
from datetime import datetime
import pandas as pd
import os

# =========================
# CARREGAR TEMPLATE
# =========================
def carregar_template(caminho):
    if not os.path.exists(caminho):
        print(f"❌ Template não encontrado: {caminho}")
        return ""
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()


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

    df = pd.DataFrame(df).copy()

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
        # PRIMEIRO ENVIO
        # =========================
        if status == "novo":
            try:
                template_email = carregar_template("templates/email_1.txt")
                if not template_email:
                    continue
                mensagem_email = template_email.replace("{cliente}", cliente)

                if "\n" in mensagem_email:
                    assunto, corpo = mensagem_email.split("\n", 1)
                    assunto = assunto.replace("Assunto: ", "")
                else:
                    assunto = "Contato Scalytech"
                    corpo = mensagem_email

                enviar_email(email, assunto, corpo)

                if telefone:
                    template_wpp = carregar_template("templates/whatsapp_1.txt")
                    if template_wpp:
                        mensagem_wpp = template_wpp.replace("{cliente}", cliente)
                        enviar_whatsapp(telefone, mensagem_wpp)

                atualizar_status(sheet if USE_GOOGLE_SHEETS else df, linha_sheet, "enviado")

            except Exception as e:
                print(f"❌ Erro ao enviar para {cliente}: {e}")

        # =========================
        # FOLLOW-UP
        # =========================
        elif status == "enviado" and pd.notna(ultimo_envio) and str(ultimo_envio).strip():
            try:
                data_envio = pd.to_datetime(ultimo_envio, errors="coerce")
                if pd.isna(data_envio):
                    continue
                dias = (datetime.now() - data_envio).days
            except Exception:
                continue

            if dias >= DIAS_FOLLOWUP:
                try:
                    template_email = carregar_template("templates/email_followup.txt")
                    if not template_email:
                        continue
                    mensagem_email = template_email.replace("{cliente}", cliente)

                    if "\n" in mensagem_email:
                        assunto, corpo = mensagem_email.split("\n", 1)
                        assunto = assunto.replace("Assunto: ", "")
                    else:
                        assunto = "Follow-up Scalytech"
                        corpo = mensagem_email

                    enviar_email(email, assunto, corpo)

                    if telefone:
                        template_wpp = carregar_template("templates/whatsapp_followup.txt")
                        if template_wpp:
                            mensagem_wpp = template_wpp.replace("{cliente}", cliente)
                            enviar_whatsapp(telefone, mensagem_wpp)

                    atualizar_status(sheet if USE_GOOGLE_SHEETS else df, linha_sheet, "followup")

                except Exception as e:
                    print(f"❌ Erro no follow-up para {cliente}: {e}")