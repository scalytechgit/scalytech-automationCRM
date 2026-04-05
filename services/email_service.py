# services/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import EMAIL, SENHA, SMTP_SERVER, SMTP_PORT

def enviar_email(destinatario: str, assunto: str, mensagem: str):
    """
    Envia um email em texto + HTML.
    Funciona local ou no Streamlit Cloud.
    """

    if not destinatario:
        print("⚠️ Destinatário vazio. Email não enviado.")
        return

    if not EMAIL or not SENHA:
        print("⚠️ Credenciais de email não configuradas. Use st.secrets ou .env")
        return

    try:
        # Monta a mensagem
        msg = MIMEMultipart()
        msg["Subject"] = assunto
        msg["From"] = EMAIL
        msg["To"] = destinatario

        # Texto plano
        texto = MIMEText(mensagem, "plain")
        # HTML
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

        # Envio
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL, SENHA)
            server.send_message(msg)

        print(f"✅ Email enviado para {destinatario}")

    except smtplib.SMTPAuthenticationError:
        print("❌ Erro de autenticação. Verifique EMAIL e SENHA ou use senha de app do Gmail.")
    except smtplib.SMTPConnectError:
        print("❌ Não foi possível conectar ao servidor SMTP.")
    except Exception as e:
        print(f"❌ Erro ao enviar email para {destinatario}: {e}")