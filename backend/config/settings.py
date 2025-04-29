import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import validator
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'echosys.db')}"  # Use absolute path
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")  # Change this in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Trace Analysis API"
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS settings
    BACKEND_CORS_ORIGINS: str = os.getenv(
        "BACKEND_CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8000,http://10.0.0.110:3000,http://127.0.0.1:3000"
    )
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Email Settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Redis Settings (for rate limiting and caching)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Database Pool Settings
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "1800"))
    
    # Database Session Settings
    DB_AUTOCOMMIT: bool = False
    DB_AUTOFLUSH: bool = False
    
    # File Upload Settings
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["json", "txt", "log"]
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    
    # RCA Settings
    RCA_MODEL_PATH: str = os.getenv("RCA_MODEL_PATH", "models/rca_model")
    RCA_THRESHOLD: float = float(os.getenv("RCA_THRESHOLD", "0.7"))
    
    # Notification Settings
    ENABLE_EMAIL_NOTIFICATIONS: bool = bool(os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "False"))
    ENABLE_SLACK_NOTIFICATIONS: bool = bool(os.getenv("ENABLE_SLACK_NOTIFICATIONS", "False"))
    SLACK_BOT_TOKEN: Optional[str] = os.getenv("SLACK_BOT_TOKEN")
    SLACK_ALERT_CHANNEL: Optional[str] = os.getenv("SLACK_ALERT_CHANNEL")
    SMTP_SERVER: Optional[str] = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM: Optional[str] = os.getenv("EMAIL_FROM")
    EMAIL_FROM_NAME: Optional[str] = os.getenv("EMAIL_FROM_NAME")
    
    # Audit Log Settings
    AUDIT_LOG_RETENTION_DAYS: int = int(os.getenv("AUDIT_LOG_RETENTION_DAYS", "90"))

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 