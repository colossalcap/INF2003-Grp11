"""
============================================================
INF2003 Group 11 — Application Configuration
Environment-based settings for PostgreSQL, MongoDB, JWT.
============================================================
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Centralized configuration loaded from environment variables."""

    # PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://ecommerce_user:ecommerce_pass@localhost:5432/ecommerce_db",
    )

    # MongoDB
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "ecommerce_nosql")

    # JWT Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    # Fraud Detection
    FRAUD_EVENT_THRESHOLD: int = int(os.getenv("FRAUD_EVENT_THRESHOLD", "10"))
    FRAUD_TIME_WINDOW_SECONDS: int = int(os.getenv("FRAUD_TIME_WINDOW_SECONDS", "60"))

    # Outbox Processor
    OUTBOX_POLL_INTERVAL_SECONDS: int = int(os.getenv("OUTBOX_POLL_INTERVAL", "5"))

    # Application
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"


settings = Settings()
