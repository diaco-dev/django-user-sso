# config.py - Configuration management
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "FioTrix SSO"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    # Environment
    ENVIRONMENT: str = "development"

    # PostgreSQL Database settings
    SSO_POSTGRES_HOST: str
    SSO_POSTGRES_PORT: int
    SSO_POSTGRES_USER: str
    SSO_POSTGRES_PASSWORD: str
    SSO_POSTGRES_DB: str
    DATABASE_URL: Optional[str] = None

    # Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # Keys
    PRIVATE_KEY_PATH: str
    PUBLIC_KEY_PATH: str

    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8001",
    ]
    OAUTH_CLIENT_ID: str
    OAUTH_CLIENT_SECRET: str
    OAUTH_REDIRECT_URI: str

    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None

    #celery
    broker_url: str = "redis://localhost:6379/1"
    result_backend: str = "redis://localhost:6379/1"

    # Email settings
    EMAIL_HOST: str = "mail.fiotrix.com"
    EMAIL_PORT: int = 587
    EMAIL_USE_TLS: bool = True
    EMAIL_HOST_USER: str = "noreply@fiotrix.com"
    EMAIL_HOST_PASSWORD: str = "Kgc668@jyD"

    farazsms_api_key: str ="GtEUrpID4Zqxvp1uqQWbXgGKorkoe9h8RSbapWPf4Zk="
    farazsms_sender: str ="+983000505"
    FARAZSMS_PATTERN_CODE:str = "x7a68g929i09924"

    # Role redirects
    ROLE_REDIRECTS: dict = {
        "admin": "http://localhost:3000/admin-dashboard",
        "staff": "http://localhost:3000/staff-dashboard",
        "user": "http://localhost:3000/user-dashboard",
    }


    class Config:
        env_file = ".env"
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Build database URLs
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql://{self.SSO_POSTGRES_USER}:{self.SSO_POSTGRES_PASSWORD}"
                f"@{self.SSO_POSTGRES_HOST}:{self.SSO_POSTGRES_PORT}/{self.SSO_POSTGRES_DB}"
            )

settings = Settings()