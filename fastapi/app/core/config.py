import os


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

    # Security
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "cup-streaming-secret-key-2024-very-secure-key-for-jwt-tokens"
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "1"))

    # Database - All from environment
    DB_NAME: str = os.getenv("DB_NAME", "cup_streaming")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres123")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")

    @property
    def DATABASE_URL(self) -> str:
        """Build DATABASE_URL from individual components"""
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # AWS S3
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "")
    S3_CUSTOM_DOMAIN: str = os.getenv("S3_CUSTOM_DOMAIN", "")

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
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "true").lower() == "true"
    FROM_EMAIL: str = os.getenv(
        "FROM_EMAIL", "Cup Streaming <noreply@cupstreaming.com>"
    )

    # Pagination
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "100"))

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Cache
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes

    # Video processing
    VIDEO_PROCESSING_QUEUE: str = os.getenv(
        "VIDEO_PROCESSING_QUEUE", "video_processing"
    )
    THUMBNAIL_SIZE: tuple = tuple(
        map(int, os.getenv("THUMBNAIL_SIZE", "320,240").split(","))
    )


settings = Settings()
