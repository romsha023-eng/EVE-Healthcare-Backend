import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "EVE Healthcare Diagnostic Booking Service"
    API_V1_STR: str = ""
    
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/eve_db"
    TEST_DATABASE_URL: Optional[str] = None
    
    JWT_SECRET: str = "super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
