from pathlib import Path
from app.core.config import settings
from app.email.template_renderer import render_email

def build_verification_email(to_email: str, otp: str) -> str:
    expiry = getattr(settings, "EMAIL_OTP_EXPIRY_MINUTES", 10)
    return render_email("verification.html", {
        "otp": otp,
        "expiry_minutes": expiry
    })

def build_password_reset_email(to_email: str, otp: str) -> str:
    expiry = getattr(settings, "PASSWORD_RESET_OTP_EXPIRY_MINUTES", 10)
    return render_email("password_reset.html", {
        "otp": otp,
        "expiry_minutes": expiry
    })

def build_password_changed_email(user_name: str) -> str:
    return render_email("password_changed.html", {
        "user_name": user_name
    })
