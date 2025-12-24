import os
from typing import List

from dotenv import load_dotenv

load_dotenv(override=True)


class Settings:
    """Runtime configuration for the authentication service."""

    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Kya Khao Auth API")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    DESCRIPTION: str = os.getenv(
        "DESCRIPTION",
        "Authentication service for the Kya Khao platform.",
    )
    API_USER_PREFIX: str = "/api/v1/user"
    API_ADMIN_PREFIX: str = "/api/v1/admin"
    API_V1_STR: str = API_USER_PREFIX  # Backwards compatibility for legacy imports

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    BASE_URL: str = os.getenv("BASE_URL") or f"http://{HOST}:{PORT}"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "changeme")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    @property
    def DATABASE_URL(self) -> str:
        url = os.getenv("DATABASE_URL")
        if not url:
            raise RuntimeError("DATABASE_URL environment variable is required.")
        return url

    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND", CELERY_BROKER_URL
    )
    REDIS_URL: str = os.getenv("REDIS_URL", CELERY_BROKER_URL)
    
    # Cache settings
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_DEFAULT_TTL: int = int(os.getenv("CACHE_DEFAULT_TTL", "3600"))  # 1 hour
    CACHE_DISH_TTL: int = int(os.getenv("CACHE_DISH_TTL", "1800"))  # 30 minutes
    CACHE_LIST_TTL: int = int(os.getenv("CACHE_LIST_TTL", "600"))  # 10 minutes
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True

    SMTP_HOST: str | None = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str | None = os.getenv("SMTP_USER")
    SMTP_PASSWORD: str | None = os.getenv("SMTP_PASSWORD")
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "true").lower() == "true"
    SMTP_SSL: bool = os.getenv("SMTP_SSL", "false").lower() == "true"
    FROM_EMAIL: str | None = os.getenv("FROM_EMAIL")
    FROM_NAME: str = os.getenv("FROM_NAME", "Kya Khao")
    EMAILS_ENABLED: bool = os.getenv("EMAILS_ENABLED", "false").lower() == "true"

    GOOGLE_CLIENT_ID: str | None = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str | None = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str | None = os.getenv("GOOGLE_REDIRECT_URI")
    GOOGLE_OAUTH_ENABLED: bool = os.getenv("GOOGLE_OAUTH_ENABLED", "false").lower() == "true"

    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_HOURS", "1"))
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = int(
        os.getenv("EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS", "24")
    )

    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        raw = os.getenv("ALLOWED_ORIGINS")
        if not raw:
            return ["*"]
        origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
        return origins or ["*"]


settings = Settings()
