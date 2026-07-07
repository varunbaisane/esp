from app.email.models import EmailMessage
from app.email.base import BaseEmailProvider

class EmailService:
    def __init__(self, provider: BaseEmailProvider):
        self.provider = provider
        
    def send(self, message: EmailMessage) -> None:
        """
        Send an email utilizing the underlying configured email provider.
        """
        self.provider.send(message)
