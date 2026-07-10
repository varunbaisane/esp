# pyrefly: ignore [missing-import]
import sib_api_v3_sdk
# pyrefly: ignore [missing-import]
from sib_api_v3_sdk.rest import ApiException

from app.email.base import BaseEmailProvider
from app.email.models import EmailMessage
from app.core.config import settings

class BrevoProvider(BaseEmailProvider):
    def __init__(self):
        configuration = sib_api_v3_sdk.Configuration()
        if not settings.BREVO_API_KEY:
            raise ValueError("BREVO_API_KEY must be configured to use BrevoProvider")
            
        configuration.api_key["api-key"] = settings.BREVO_API_KEY
        
        self.api = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        
    def send(self, message: EmailMessage) -> None:
        # TODO: 
        # Move email delivery to asynchronous jobs once Redis is introduced.
        # Future:
        # - retry with exponential backoff
        # - idempotency key
        # - background queue (Redis)
        
        sender = {
            "name": settings.EMAIL_FROM_NAME,
            "email": settings.EMAIL_FROM_ADDRESS,
        }
        
        to = [{"email": email} for email in message.to]
        cc = [{"email": email} for email in message.cc] if message.cc else None
        bcc = [{"email": email} for email in message.bcc] if message.bcc else None
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender=sender,
            to=to,
            cc=cc,
            bcc=bcc,
            subject=message.subject,
            html_content=message.html if message.html else None,
            text_content=message.text if not message.html else None
        )
        
        try:
            self.api.send_transac_email(send_smtp_email)
        except ApiException as e:
            raise RuntimeError(f"Failed to send email via Brevo API: {e}")
