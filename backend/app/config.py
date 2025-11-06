"""
Application Configuration
使用 Pydantic Settings 管理環境變數
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator
import json


class Settings(BaseSettings):
    """應用程式設定"""

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/propulseiq"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI Service
    ANTHROPIC_API_KEY: str = ""
    AI_MODEL: str = "claude-3-5-sonnet-20241022"
    AI_MAX_RETRIES: int = 3
    AI_BATCH_SIZE: int = 5
    AI_DAILY_QUOTA: int = 1000

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # App
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "PropulseIQ"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Rate Limiting (requests per day)
    API_RATE_LIMIT_FREE: int = 100
    API_RATE_LIMIT_PRO: int = 5000
    API_RATE_LIMIT_BUSINESS: int = 50000

    # Content Retention
    RAW_CONTENT_RETENTION_DAYS: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


# 建立全域設定實例
settings = Settings()
