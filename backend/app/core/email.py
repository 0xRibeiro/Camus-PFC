from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings


# manda um email de texto simples pelo smtp configurado 
async def enviar_email(destinatario: str, assunto: str, corpo: str) -> None:
    mensagem = EmailMessage()
    mensagem["From"] = settings.smtp_user
    mensagem["To"] = destinatario
    mensagem["Subject"] = assunto
    mensagem.set_content(corpo)

    await aiosmtplib.send(
        mensagem,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_password,
        start_tls=True,
    )