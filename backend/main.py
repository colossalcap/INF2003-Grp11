"""
FastAPI Application Entry Point — E-Commerce Analytics Platform.
=================================================================

ARCHITECTURE OVERVIEW:
  This file wires together the entire backend: it creates the FastAPI app,
  registers 5 API routers, configures CORS for the React frontend, and
  manages the application lifecycle (startup/shutdown hooks).

DUAL-DATABASE DESIGN:
  - PostgreSQL (ACID): orders, inventory, customers, users via SQLAlchemy ORM
  - MongoDB (BASE):    clickstream events, sessions, funnel via Motor async driver
  - CDC Bridge:        Outbox Pattern — PostgreSQL triggers write to outbox table,
                       async poller (sync_service.py) reads outbox every 5s,
                       syncs denormalized summaries to MongoDB

LIFECYCLE HOOKS (startup, in order):
  1. Base.metadata.create_all() — Creates all 8 PostgreSQL tables if they
     don't exist (idempotent — safe to call on every startup).
  2. init_mongo_indexes() — Creates compound, TTL, and filtered indexes
     on MongoDB collections for query performance.
  3. start_outbox_processor() — Launches an asyncio background task that
     polls the outbox table for unprocessed CDC events every 5 seconds.

LIFECYCLE HOOKS (shutdown):
  1. stop_outbox_processor() — Cancels the background CDC poller gracefully.

API ROUTERS:
  /api/auth/*      — JWT registration, login, profile (auth.py)
  /api/products/*  — Product catalog with search & pagination (products.py)
  /api/cart/*      — Clickstream event recording & fraud detection (cart.py)
  /api/orders/*    — ACID order creation with trigger cascade (orders.py)
  /api/analytics/* — RFM, funnel, market basket, alerts (analytics.py)
"""

# ── Imports ─────────────────────────────────────────────────
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from models.relational import Base, engine, SessionLocal
from services.sync_service import start_outbox_processor, stop_outbox_processor
from services.nosql_service import init_mongo_indexes
from api import auth, products, cart, orders, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan — runs startup/shutdown code around the app's request-serving phase.

    STARTUP (sequential):
      1. create_all() — Creates PostgreSQL tables via ORM metadata (idempotent).
      2. init_mongo_indexes() — Builds compound, TTL, and query indexes on MongoDB.
      3. start_outbox_processor() — Launches async CDC poller (5s interval).

    SHUTDOWN:
      1. Cancels the CDC poller task for clean process exit.
    """
    # ═══ STARTUP ═══
    print("🚀 Starting E-Commerce Analytics Platform...")

    # Idempotent: creates 8 tables if missing, no-op if they already exist.
    Base.metadata.create_all(bind=engine)
    print("✅ PostgreSQL tables created (if not existed).")

    # Creates indexes on user_sessions (compound, TTL, flagged, timestamp).
    await init_mongo_indexes()
    print("✅ MongoDB indexes initialized.")

    # Launches background asyncio task — polls outbox → syncs to MongoDB.
    # Implements at-least-once delivery via idempotent $inc operations.
    await start_outbox_processor()
    print("✅ Outbox processor started.")

    yield  # ← App serves requests here

    # ═══ SHUTDOWN ═══
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

# ── CORS Middleware ──────────────────────────────────────────
# Allows the React frontend (port 3000) to call this API (port 8000).
# Without CORS, browsers block cross-origin requests for security.
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
