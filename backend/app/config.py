"""
Configuration settings for the Veteran Referral Portal API
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "Veteran Referral Portal API"
    debug: bool = True  # Enable debug mode for development
    version: str = "1.0.0"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = ["*"]  # Restrict in production
    allowed_hosts: List[str] = ["*"]    # Restrict in production
    
    # Database
    database_url: str = "postgresql://vrp_admin:password@localhost:5432/veteran_referral_portal"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # AWS
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = [".csv"]
    
    # Logging
    log_level: str = "INFO"
    
    # PII Detection
    pii_detection_enabled: bool = True
    pii_patterns: List[str] = [
        r'\\b\\d{3}-\\d{2}-\\d{4}\\b',  # SSN
        r'\\b\\d{3}-\\d{3}-\\d{4}\\b',  # Phone numbers (XXX-XXX-XXXX)
        r'\\b\\d{10}\\b',                # Phone numbers (10 digits)
        r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b',  # Email
        r'\\b[A-Za-z]+ [A-Za-z]+\\b'   # Names (basic)
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Load settings from environment
settings = Settings()

# Override database URL if environment variable is set
if os.getenv("DATABASE_URL"):
    settings.database_url = os.getenv("DATABASE_URL")

# Override AWS credentials if environment variables are set
if os.getenv("AWS_ACCESS_KEY_ID"):
    settings.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
if os.getenv("AWS_SECRET_ACCESS_KEY"):
    settings.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
