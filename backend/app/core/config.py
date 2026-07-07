from pydantic_settings import BaseSettings, SettingsConfigDict  # pyrefly: ignore [missing-import]
from app.core.db_config import DatabaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Engineering Support Platform"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: str = "http://localhost:5173"
    
    # Notification Channels
    EMAIL_PROVIDER: str = "console"
    EMAIL_FROM_NAME: str = "Engineering Support Platform"
    EMAIL_FROM_ADDRESS: str = "no-reply@example.com"
    
    # SMTP Config
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
db_settings = DatabaseSettings()
