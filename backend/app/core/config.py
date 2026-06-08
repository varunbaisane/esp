from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Engineering Support Platform"
    API_V1_PREFIX: str = "/api/v1"

settings = Settings()
