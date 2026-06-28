from pydantic_settings import BaseSettings, SettingsConfigDict  # pyrefly: ignore [missing-import]
import os

class EmailConfig(BaseSettings):
    EMAIL_MODE: str = "mock"
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_TLS: bool = True
    
    # Expiry Settings
    EMAIL_OTP_EXPIRY_MINUTES: int = 10
    PASSWORD_RESET_OTP_EXPIRY_MINUTES: int = 10
    ACCOUNT_VERIFICATION_EXPIRY_MINUTES: int = 15
    
    # Auth
    REMEMBER_ME_EXPIRE_DAYS: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

email_settings = EmailConfig()
