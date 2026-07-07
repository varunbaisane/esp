from app.email.base import BaseEmailProvider
from app.email.models import EmailMessage
from app.core.config import settings

class ConsoleProvider(BaseEmailProvider):
    def send(self, message: EmailMessage) -> None:
        print("=" * 60)
        print("EMAIL SIMULATION (ConsoleProvider)")
        print("=" * 60)
        print(f"From:    {settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM_ADDRESS}>")
        print(f"To:      {', '.join(message.to)}")
        if message.cc:
            print(f"Cc:      {', '.join(message.cc)}")
        if message.bcc:
            print(f"Bcc:     {', '.join(message.bcc)}")
        print(f"Subject: {message.subject}")
        print("-" * 60)
        
        if message.text:
            print("[TEXT BODY]")
            print(message.text)
            
        if message.html:
            if message.text:
                print("\n[HTML BODY]")
            print(message.html)
            
        print("=" * 60)
