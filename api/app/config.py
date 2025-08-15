# api/app/config.py
from dotenv import load_dotenv
load_dotenv()  # Load variables from .env for local dev before reading them

import os

class Settings:
    DEV_SKIP_AUTH: bool = os.getenv("DEV_SKIP_AUTH", "false").lower() == "true"
    PORT: int = int(os.getenv("PORT", "8080"))
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "changeme")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "43200"))  # 30 days
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRICE_MONTHLY: str = os.getenv("STRIPE_PRICE_MONTHLY", "")
    STRIPE_PRICE_QUARTERLY: str = os.getenv("STRIPE_PRICE_QUARTERLY", "")
    STRIPE_PRICE_YEARLY: str = os.getenv("STRIPE_PRICE_YEARLY", "")
    APP_BASE_URL: str = os.getenv("APP_BASE_URL", "http://localhost:3000")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8080")

settings = Settings()
