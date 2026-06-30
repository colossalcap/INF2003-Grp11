"""
Centralized Application Configuration for the E-Commerce Analytics Platform.
============================================================================

Loads settings from environment variables (12-Factor App methodology).
All sensitive values are injected at runtime via Docker Compose or .env file
— never hardcoded in source. Each setting has a sensible localhost default
that is automatically overridden in Docker by the docker-compose.yml
environment block.

CONFIGURATION GROUPS:
  1. PostgreSQL — Relational DB for ACID transactions (orders, inventory)
  2. MongoDB    — Document store for high-velocity clickstream (BASE)
  3. JWT        — Stateless authentication tokens (HMAC-SHA256)
  4. Fraud      — Velocity-check thresholds for cart-abuse detection
  5. Outbox     — CDC bridge polling interval (PostgreSQL → MongoDB)
  6. App        — Debug mode toggle

WHY LOCALHOST DEFAULTS + DOCKER OVERRIDES:
  Local dev assumes native PostgreSQL/MongoDB on localhost.
  Docker Compose sets host=postgres / host=mongodb (service names),
  which override the defaults automatically at container startup.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Centralized, typed configuration singleton.

    Reads all values from os.getenv(KEY, default). Docker Compose injects
    production values via the container environment; local dev uses defaults.
    """

    # ── PostgreSQL (Relational / ACID) ──────────────────────
    # Connection string: postgresql://user:pass@host:port/db
    # Docker override: host='postgres' via docker-compose.yml
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://ecommerce_user:ecommerce_pass@localhost:5432/ecommerce_db",
    )

    # ── MongoDB (NoSQL / BASE) ─────────────────────────────
    # Async connection via Motor driver. Docker override: host='mongodb'
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "ecommerce_nosql")

    # ── JWT Authentication ──────────────────────────────────
    # HMAC-SHA256 signed tokens. SECRET_KEY MUST be changed in production.
    # Tokens expire after EXPIRE_MINUTES (default: 60 min).
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    # ── Fraud Detection ────────────────────────────────────
    # If a user fires ≥THRESHOLD add_to_cart events within
    # TIME_WINDOW_SECONDS without a purchase → flagged as fraud.
    FRAUD_EVENT_THRESHOLD: int = int(os.getenv("FRAUD_EVENT_THRESHOLD", "10"))
    FRAUD_TIME_WINDOW_SECONDS: int = int(os.getenv("FRAUD_TIME_WINDOW_SECONDS", "60"))

    # ── Outbox Pattern / CDC ───────────────────────────────
    # Background poller checks the outbox table every N seconds
    # for unprocessed events → syncs to MongoDB (at-least-once).
    OUTBOX_POLL_INTERVAL_SECONDS: int = int(os.getenv("OUTBOX_POLL_INTERVAL", "5"))

    # ── Application ────────────────────────────────────────
    # When True, SQLAlchemy echoes all SQL queries to stdout.
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"


# Module-level singleton — import as `from config import settings`
settings = Settings()


settings = Settings()
