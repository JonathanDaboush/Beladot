"""
Application Configuration Module

Manages all environment-specific settings using Pydantic Settings.
Configuration is loaded from .env file with sensible defaults.

Environment Variables:
    - DATABASE_URL: Async PostgreSQL connection string (asyncpg)
    - DATABASE_URL_SYNC: Sync PostgreSQL connection string (psycopg2)
    - SECRET_KEY: JWT signing key (generate with: secrets.token_urlsafe(32))
    - ENVIRONMENT: development, staging, or production
    - All other settings documented below

Usage:
    from config import Settings
    settings = Settings()
    db_url = settings.DATABASE_URL
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via .env file or environment variables.
    Required settings must be provided or application will fail to start.
    """
    
    # ========================================================================
    # DATABASE CONFIGURATION
    # ========================================================================
    DATABASE_URL: str  # Required: postgresql+asyncpg://user:pass@host:port/db
    DATABASE_URL_SYNC: str  # Required: postgresql://user:pass@host:port/db (for migrations)
    
    # ========================================================================
    # JWT AUTHENTICATION
    # ========================================================================
    SECRET_KEY: str  # Required: Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
    ALGORITHM: str = "HS256"  # JWT signing algorithm (HS256, HS384, HS512)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Short-lived access token lifetime
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Refresh token lifetime
    
    # ========================================================================
    # SERVER CONFIGURATION
    # ========================================================================
    HOST: str = "0.0.0.0"  # Bind address (0.0.0.0 = all interfaces)
    PORT: int = 8000  # Server port
    DEBUG: bool = True  # Enable debug mode (MUST be False in production)
    ENVIRONMENT: str = "development"  # Environment: development, staging, production
    
    # ========================================================================
    # CORS (Cross-Origin Resource Sharing)
    # ========================================================================
    CORS_ORIGINS: str = "http://localhost:3000"  # Comma-separated allowed origins
    
    @property
    def allowed_origins(self) -> List[str]:
        """Parse CORS_ORIGINS string into list of allowed origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def allowed_hosts(self) -> List[str]:
        """Extract hostnames from allowed origins for TrustedHost middleware."""
        hosts = []
        for origin in self.allowed_origins:
            # Extract hostname from URL
            if "://" in origin:
                host = origin.split("://")[1].split(":")[0]
                hosts.append(host)
        return hosts if hosts else ["localhost", "127.0.0.1"]
    
    # ========================================================================
    # REDIS (Caching & Rate Limiting)
    # ========================================================================
    REDIS_URL: str = "redis://localhost:6379/0"  # Redis connection string
    
    # ========================================================================
    # EMAIL CONFIGURATION (Optional)
    # ========================================================================
    SMTP_HOST: str = ""  # SMTP server hostname (e.g., smtp.gmail.com)
    SMTP_PORT: int = 587  # SMTP port (587 for TLS, 465 for SSL)
    SMTP_USER: str = ""  # SMTP username/email
    SMTP_PASSWORD: str = ""  # SMTP password/app password
    
    # ========================================================================
    # PAYMENT GATEWAY (Optional)
    # ========================================================================
    PAYMENT_GATEWAY_API_KEY: str = ""  # Payment processor API key
    
    # ========================================================================
    # SHIPPING CONFIGURATION
    # ========================================================================
    # Internal shipping tracking only - no external carrier APIs
    # All shipments are managed within the application database
    DEFAULT_CARRIER: str = "purolator"  # Default carrier for auto-selection
    AVAILABLE_CARRIERS: List[str] = ["purolator", "fedex", "dhl", "ups", "canadapost"]
    
    # ========================================================================
    # AWS S3 (Optional - for file/image storage)
    # ========================================================================
    AWS_ACCESS_KEY_ID: str = ""  # AWS access key
    AWS_SECRET_ACCESS_KEY: str = ""  # AWS secret key
    AWS_BUCKET_NAME: str = ""  # S3 bucket name for uploads
    AWS_REGION: str = "us-east-1"  # AWS region
    
    class Config:
        """Pydantic configuration for settings loading."""
        env_file = ".env"  # Load settings from .env file
        case_sensitive = False  # Environment variables are case-insensitive
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
