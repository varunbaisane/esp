from app.core.config import settings
from app.email.base import BaseEmailProvider
from app.email.console_provider import ConsoleProvider
from app.email.smtp_provider import SMTPProvider
from app.email.brevo_provider import BrevoProvider

def get_email_provider() -> BaseEmailProvider:
    provider = settings.EMAIL_PROVIDER.lower()
    
    if provider == "console":
        return ConsoleProvider()
    elif provider == "smtp":
        return SMTPProvider()
    elif provider == "brevo":
        return BrevoProvider()
    else:
        raise ValueError(f"Unknown EMAIL_PROVIDER configuration: {provider}")
