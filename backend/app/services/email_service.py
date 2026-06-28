import smtplib
from email.message import EmailMessage
from pathlib import Path

from fastapi import BackgroundTasks  # pyrefly: ignore [missing-import]
from app.core.email_config import email_settings

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "emails"

class EmailService:
    @staticmethod
    def _send_email_sync(to_email: str, subject: str, html_content: str) -> None:
        if email_settings.EMAIL_MODE == "mock":
            print("==========================================")
            print("EMAIL SENT")
            print()
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print()
            print("Mode: MOCK")
            print()
            print("Status: SUCCESS")
            print("==========================================")
            return

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = email_settings.SMTP_FROM
        msg["To"] = to_email
        msg.add_alternative(html_content, subtype="html")

        try:
            with smtplib.SMTP(email_settings.SMTP_HOST, email_settings.SMTP_PORT) as server:
                if email_settings.SMTP_TLS:
                    server.starttls()
                if email_settings.SMTP_USERNAME and email_settings.SMTP_PASSWORD:
                    server.login(email_settings.SMTP_USERNAME, email_settings.SMTP_PASSWORD)
                server.send_message(msg)
            print("==========================================")
            print("EMAIL SENT")
            print()
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print()
            print("Mode: SMTP")
            print()
            print("Status: SUCCESS")
            print("==========================================")
        except Exception as e:
            print("==========================================")
            print("EMAIL FAILED")
            print()
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print()
            print("Mode: SMTP")
            print()
            print(f"Error: {e}")
            print("==========================================")
            raise e

    @staticmethod
    def send_verification_otp(to_email: str, otp: str) -> None:
        template_path = TEMPLATES_DIR / "verification.html"
        html_content = template_path.read_text(encoding="utf-8")
        html_content = html_content.replace("{otp}", otp)
        html_content = html_content.replace("{expiry_minutes}", str(email_settings.EMAIL_OTP_EXPIRY_MINUTES))
        
        EmailService._send_email_sync(
            to_email,
            "Verify your Email Address",
            html_content
        )

    @staticmethod
    def send_password_reset_otp(to_email: str, otp: str) -> None:
        template_path = TEMPLATES_DIR / "password_reset.html"
        html_content = template_path.read_text(encoding="utf-8")
        html_content = html_content.replace("{otp}", otp)
        html_content = html_content.replace("{expiry_minutes}", str(email_settings.PASSWORD_RESET_OTP_EXPIRY_MINUTES))
        
        EmailService._send_email_sync(
            to_email,
            "Reset your Password",
            html_content
        )
