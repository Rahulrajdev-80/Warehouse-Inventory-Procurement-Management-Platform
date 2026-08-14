import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Warehouse Inventory & Procurement Platform"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    SECRET_KEY: str = "supersecretjwtkeyforwarehouseinventoryprocurementplatformchangeinprod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "warehouse_db"
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/warehouse_db"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/warehouse_db"
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379/0"
    
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "noreply@warehouseinventory.com"
    SMTP_PASSWORD: str = "password"
    EMAILS_FROM_EMAIL: str = "noreply@warehouseinventory.com"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
