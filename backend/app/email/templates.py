from pathlib import Path
from app.core.config import settings

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "emails"

def build_verification_email(to_email: str, otp: str) -> str:
    template_path = TEMPLATES_DIR / "verification.html"
    html_content = template_path.read_text(encoding="utf-8")
    html_content = html_content.replace("{otp}", otp)
    
    # Ideally from config, but hardcoding fallback if not in settings
    expiry = getattr(settings, "EMAIL_OTP_EXPIRY_MINUTES", 10)
    html_content = html_content.replace("{expiry_minutes}", str(expiry))
    return html_content

def build_password_reset_email(to_email: str, otp: str) -> str:
    template_path = TEMPLATES_DIR / "password_reset.html"
    html_content = template_path.read_text(encoding="utf-8")
    html_content = html_content.replace("{otp}", otp)
    
    expiry = getattr(settings, "PASSWORD_RESET_OTP_EXPIRY_MINUTES", 10)
    html_content = html_content.replace("{expiry_minutes}", str(expiry))
    return html_content
