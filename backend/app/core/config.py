from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.db_config import DatabaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Engineering Support Platform"
    API_V1_PREFIX: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
db_settings = DatabaseSettings()
