import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import EMAIL, SENHA, SMTP_SERVER, SMTP_PORT
from config.settings import USE_GOOGLE_SHEETS, SHEET_NAME


def enviar_email(destinatario, assunto, mensagem):
    try:
        # =========================
        # MONTAR EMAIL (HTML + TEXTO)
        # =========================
        msg = MIMEMultipart()
        msg["Subject"] = assunto
        msg["From"] = EMAIL
        msg["To"] = destinatario

        # versão texto
        texto = MIMEText(mensagem, "plain")

        # versão HTML (melhor aparência)
        html = MIMEText(f"""
        <html>
            <body>
                <p>{mensagem.replace("\n", "<br>")}</p>
                <br>
                <p><strong>Scalytech</strong><br>
                Tecnologia que automatiza, cresce e escala.</p>
            </body>
        </html>
        """, "html")

        msg.attach(texto)
        msg.attach(html)

        # =========================
        # ENVIO
        # =========================
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, SENHA)
            server.send_message(msg)

        print(f"✅ Email enviado para {destinatario}")

    except Exception as e:
        print(f"❌ Erro ao enviar email para {destinatario}: {e}")