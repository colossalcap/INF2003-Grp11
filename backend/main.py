"""
============================================================
INF2003 Group 11 — E-Commerce Clickstream & Transaction Analytics
FastAPI Application Entry Point
============================================================
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from config import settings
from models.relational import Base, engine, SessionLocal
from services.sync_service import start_outbox_processor, stop_outbox_processor
from services.nosql_service import init_mongo_indexes
from api import auth, products, cart, orders, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan: startup/shutdown hooks.
    - Creates relational tables on startup.
    - Initializes MongoDB indexes.
    - Starts the Outbox Pattern background processor.
    """
    # === Startup ===
    print("🚀 Starting E-Commerce Analytics Platform...")

    # Create relational tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("✅ PostgreSQL tables created (if not existed).")

    # Initialize MongoDB indexes
    await init_mongo_indexes()
    print("✅ MongoDB indexes initialized.")

    # Start Outbox Processor (CDC via Outbox Pattern)
    await start_outbox_processor()
    print("✅ Outbox processor started.")

    yield  # Application runs here

    # === Shutdown ===
    await stop_outbox_processor()
    print("🛑 Outbox processor stopped.")


app = FastAPI(
    title="E-Commerce Analytics Platform",
    description="Dual-database system: PostgreSQL (transactions) + MongoDB (clickstream). "
                "Demonstrates ACID vs BASE, triggers, CDC/Outbox, RFM segmentation, "
                "market basket analysis, and funnel analytics.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart & Clickstream"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "E-Commerce Analytics Platform API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check for Docker monitoring."""
    try:
        # Check PostgreSQL
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        pg_status = "healthy"
    except Exception:
        pg_status = "unhealthy"

    return {
        "postgres": pg_status,
        "mongodb": "healthy",  # Assumes connection was successful at startup
    }
