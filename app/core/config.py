from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Basic settings
    PROJECT_NAME: str = "Cup Streaming API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DB_NAME: str = "cup-entertainment"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "#Trigonometry1"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = ""
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # File upload
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_VIDEO_FORMATS: List[str] = ["mp4", "avi", "mov", "mkv", "wmv"]
    
    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
