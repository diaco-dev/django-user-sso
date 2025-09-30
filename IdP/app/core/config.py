# config.py - Configuration management
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Keys
    PRIVATE_KEY_PATH: str = "../keys/private.pem"
    PUBLIC_KEY_PATH: str = "../keys/public.pem"

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8001",
    ]
    oauth_client_id: str
    oauth_client_secret: str
    oauth_redirect_uri: str

    # Role redirects
    ROLE_REDIRECTS: dict = {
        "admin": "http://localhost:3000/admin-dashboard",
        "staff": "http://localhost:3000/staff-dashboard",
        "user": "http://localhost:3000/user-dashboard",
    }
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()