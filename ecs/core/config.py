from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    
    # Application settings
    TITLE: str = "Empathic Credit System API"
    
    # Auth
    JWT_SECRET_KEY: str = "644383a7231214b5cc072ccac0a678d1"
    JWT_EXPIRES_IN: timedelta = timedelta(seconds=3600)
    JWT_ALGORITHM: str = "HS256"

    # Database
    DB_URL: str = ""

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Settings() # type: ignore