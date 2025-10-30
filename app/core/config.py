import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.getenv("ENV_FILE", ".env"))


class Settings:
    # Required hardcoded values
    PROJECT_NAME: str = "Cup Streaming API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = (
        "A modern, high-performance video streaming platform built with FastAPI"
    )
    API_V1_STR: str = "/api/v1"

    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    BASE_URL: str = os.getenv("BASE_URL")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "1"))

    # Database - All from environment
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))

    @property
    def DATABASE_URL(self) -> str:
        """Build DATABASE_URL from individual components"""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/0"
    )
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: list[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True

    # AWS S3
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION")
    S3_BUCKET: str = os.getenv("S3_BUCKET")
    S3_CUSTOM_DOMAIN: str = os.getenv("S3_CUSTOM_DOMAIN")

    # CORS
    ALLOWED_HOSTS: list[str] = (
        os.getenv("ALLOWED_HOSTS", "*").split(",")
        if os.getenv("ALLOWED_HOSTS")
        else ["*"]
    )
    ALLOWED_ORIGINS: list[str] = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:3001,"
        "http://127.0.0.1:3000,http://127.0.0.1:3001,"
        "http://localhost:8000,http://localhost:8001",
    ).split(",")

    # File upload
    MAX_FILE_SIZE: int = int(
        os.getenv("MAX_FILE_SIZE", str(100 * 1024 * 1024))
    )  # 100MB
    ALLOWED_VIDEO_FORMATS: list[str] = os.getenv(
        "ALLOWED_VIDEO_FORMATS", "mp4,avi,mov,mkv,wmv,webm"
    ).split(",")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")

    # Email - All from environment
    SMTP_HOST: str = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "true").lower() == "true"
    SMTP_SSL: bool = os.getenv("SMTP_SSL", "false").lower() == "true"
    FROM_EMAIL: str = os.getenv("FROM_EMAIL")
    FROM_NAME: str = os.getenv("FROM_NAME", "Cup Streaming")
    EMAILS_ENABLED: bool = os.getenv("EMAILS_ENABLED", "false").lower() == "true"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI")
    GOOGLE_OAUTH_ENABLED: bool = (
        os.getenv("GOOGLE_OAUTH_ENABLED", "false").lower() == "true"
    )

    # Token settings
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = int("1")
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = int("24")

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 15  # Default requests per minute

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Cache
    CACHE_TTL: int = 300

    # Video processing
    VIDEO_PROCESSING_QUEUE: str = os.getenv(
        "VIDEO_PROCESSING_QUEUE", "video_processing"
    )
    THUMBNAIL_SIZE: tuple = tuple(
        map(int, os.getenv("THUMBNAIL_SIZE", "320,240").split(","))
    )

    AVATAR_ALLOWED_FILE_TYPES = [".jpg", ".jpeg", ".png", ".webp", ".gif"]

    # ✅ NEW: Retry and Throttling Configuration
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "5/minute")  # used by SlowAPI
    RETRY_ATTEMPTS: int = int(os.getenv("RETRY_ATTEMPTS", 3))
    RETRY_DELAY: float = float(os.getenv("RETRY_DELAY", 1.0))  # seconds
    RETRY_BACKOFF: float = float(os.getenv("RETRY_BACKOFF", 2.0))  # exponential backoff


settings = Settings()
