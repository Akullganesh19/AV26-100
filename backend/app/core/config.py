import logging
import sys
from typing import List, Union, Optional, Any

from pydantic import AnyHttpUrl, field_validator, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    ENVIRONMENT: str = "development"  # development, staging, production

    # Celery & Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    CELERY_BROKER_URL: RedisDsn = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: RedisDsn = "redis://localhost:6379/0"
    CLERK_PEM_PUBLIC_KEY: str = ""
    CLERK_ISSUER: str = ""
    CLERK_AUDIENCE: str = ""

    PROJECT_NAME: str = "EpiSense"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api"

    # Database
    DATABASE_URL: PostgresDsn

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        if isinstance(v, (list, str)):
            return v
        return v

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASS: Optional[str] = None

    # ML & APIs
    OPENMETEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    MLFLOW_TRACKING_URI: Optional[str] = None
    ALERT_THRESHOLD_DEFAULT: int = 70
    
    CLINICAL_MANIFEST_PATH: str = "app/core/manifest.json"
    CLINICAL_MODELS_DIR: str = "../integrated_diagnostics/Saved_Models"

    # Logging
    LOG_LEVEL: str = "INFO"

    # API Keys
    ALGOLIA_API_KEY: Optional[str] = None
    SENDGRID_API_KEY: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    CLERK_SECRET_KEY: Optional[str] = None
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: Optional[str] = None


settings = Settings()

# Setup logging (handled by structlog in main.py)
logger = logging.getLogger(settings.PROJECT_NAME)
