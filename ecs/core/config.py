import logging
import os
from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    
    # Application settings
    TITLE: str = "Empathic Credit System API"
    
    # Environment settings
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    
    LOG_LEVEL: str = "info"
    
    # Auth
    JWT_SECRET_KEY: str = ""
    JWT_EXPIRES_SECONDS: int = 3600
    JWT_ALGORITHM: str = ""

    # Database
    DB_URL: str = ""
    REDIS_URL: str = ""

    # Feature engineering configuration
    feature_engineering_transactions_period_days: int = 30
    feature_engineering_transactions_limit: int = 1000
    feature_engineering_emotional_events_period_days: int = 7
    feature_engineering_emotional_events_limit: int = 50

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() in ["development", "dev"]
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in ["production", "prod"]
    
    @property
    def should_include_error_details(self) -> bool:
        """Whether to show detailed error information to clients"""
        return self.DEBUG and self.is_development

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra="allow")

settings = Settings() # type: ignore