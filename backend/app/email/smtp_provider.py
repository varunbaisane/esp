import smtplib
from email.message import EmailMessage as StdEmailMessage
from email.utils import formataddr

from app.email.base import BaseEmailProvider
from app.email.models import EmailMessage
from app.core.config import settings

class SMTPProvider(BaseEmailProvider):
    def send(self, message: EmailMessage) -> None:
        if not settings.SMTP_HOST or not settings.SMTP_PORT:
            raise ValueError("SMTP_HOST and SMTP_PORT must be configured for SMTPProvider")
            
        msg = StdEmailMessage()
        msg['Subject'] = message.subject
        msg['From'] = formataddr((settings.EMAIL_FROM_NAME, settings.EMAIL_FROM_ADDRESS))
        msg['To'] = ", ".join(message.to)
        
        if message.cc:
            msg['Cc'] = ", ".join(message.cc)
        if message.bcc:
            msg['Bcc'] = ", ".join(message.bcc)
            
        if message.text and message.html:
            # Multipart
            msg.set_content(message.text)
            msg.add_alternative(message.html, subtype='html')
        elif message.html:
            msg.set_content(message.html, subtype='html')
        elif message.text:
            msg.set_content(message.text)
        else:
            msg.set_content("") # Empty email
            
        # Connect and send
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            
            server.send_message(msg)
