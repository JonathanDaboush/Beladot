from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Email (optional)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Payment
    PAYMENT_GATEWAY_API_KEY: str = ""
    
    # Shipping Carriers (PROOF OF CONCEPT - MOCK MODE)
    # All carrier integrations are simulated - no real API calls are made
    # This system tracks company deliveries/imports/exports internally
    
    # Purolator (MOCK)
    PUROLATOR_API_KEY: str = "mock-key"
    PUROLATOR_API_SECRET: str = "mock-secret"
    PUROLATOR_ACCOUNT_NUMBER: str = "mock-account"
    PUROLATOR_BASE_URL: str = "https://webservices.purolator.com/PWS/V2"
    PUROLATOR_WEBHOOK_SECRET: str = "mock-webhook-secret"
    
    # FedEx (MOCK)
    FEDEX_API_KEY: str = "mock-key"
    FEDEX_SECRET_KEY: str = "mock-secret"
    FEDEX_ACCOUNT_NUMBER: str = "mock-account"
    FEDEX_METER_NUMBER: str = "mock-meter"
    FEDEX_BASE_URL: str = "https://apis.fedex.com"
    FEDEX_WEBHOOK_SECRET: str = "mock-webhook-secret"
    
    # DHL (MOCK)
    DHL_API_KEY: str = "mock-key"
    DHL_API_SECRET: str = "mock-secret"
    DHL_ACCOUNT_NUMBER: str = "mock-account"
    DHL_BASE_URL: str = "https://api.dhl.com"
    DHL_WEBHOOK_SECRET: str = "mock-webhook-secret"
    
    # UPS (MOCK)
    UPS_CLIENT_ID: str = "mock-client-id"
    UPS_CLIENT_SECRET: str = "mock-secret"
    UPS_ACCOUNT_NUMBER: str = "mock-account"
    UPS_BASE_URL: str = "https://onlinetools.ups.com/api"
    UPS_WEBHOOK_SECRET: str = "mock-webhook-secret"
    
    # Canada Post (MOCK)
    CANADAPOST_API_KEY: str = "mock-key"
    CANADAPOST_API_SECRET: str = "mock-secret"
    CANADAPOST_CUSTOMER_NUMBER: str = "mock-customer"
    CANADAPOST_BASE_URL: str = "https://ct.soa-gw.canadapost.ca"
    
    # Shipping Configuration
    MOCK_MODE: bool = True  # Simulate carrier responses without API calls
    DEFAULT_CARRIER: str = "purolator"
    ENABLE_CARRIER_RATE_SHOPPING: bool = True
    TRACKING_SYNC_INTERVAL_MINUTES: int = 15
    
    # AWS S3 (optional)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_BUCKET_NAME: str = ""
    AWS_REGION: str = "us-east-1"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
