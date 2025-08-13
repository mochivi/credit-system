import logging
from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    
    # Application settings
    TITLE: str = "Empathic Credit System API"

    LOG_LEVEL: str = "info"
    
    # Auth
    JWT_SECRET_KEY: str = ""
    JWT_EXPIRES_SECONDS: int = 3600
    JWT_ALGORITHM: str = ""

    # Database
    DB_URL: str = ""
    REDIS_URL: str = ""

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra="allow")

settings = Settings() # type: ignore