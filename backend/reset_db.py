"""
============================================================
INF2003 Group 11 — Database Reset Script
Drops all data from PostgreSQL and MongoDB.
Run via: docker-compose --profile reset up reset-db
============================================================
"""

import asyncio
import sys

from sqlalchemy import text
from models.relational import engine, Base

sys.path.insert(0, "/app")


def reset_postgresql():
    """Drop and recreate all PostgreSQL tables."""
    print("🗑️  Dropping all PostgreSQL tables...")

    # Drop all tables in correct order (respect FK constraints)
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS order_audit_log CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS alerts CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS outbox CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS order_items CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS orders CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS products CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS customers CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        conn.commit()
        print("   ✅ Tables dropped.")

    # Recreate all tables from SQLAlchemy models
    Base.metadata.create_all(bind=engine)
    print("   ✅ Tables recreated from ORM models.")

    # Re-run trigger definitions from triggers.sql
    import os
    triggers_path = "/app/triggers.sql"
    if os.path.exists(triggers_path):
        with open(triggers_path) as f:
            sql = f.read()
        with engine.connect() as conn:
            # Execute each statement individually
            for statement in sql.split(";"):
                statement = statement.strip()
                if statement and not statement.startswith("--"):
                    try:
                        conn.execute(text(statement))
                    except Exception as e:
                        # Skip "already exists" errors from CREATE IF NOT EXISTS
                        if "already exists" not in str(e).lower():
                            print(f"   ⚠️  Skipped: {e}")
            conn.commit()
        print("   ✅ Triggers re-applied.")

    print("✅ PostgreSQL reset complete.\n")


async def reset_mongodb():
    """Drop all MongoDB collections."""
    from services.nosql_service import get_mongo_db

    print("🗑️  Dropping all MongoDB collections...")

    db = await get_mongo_db()
    collections = await db.list_collection_names()

    for col in collections:
        await db.drop_collection(col)
        print(f"   ✅ Dropped: {col}")

    # Re-initialize indexes
    from services.nosql_service import init_mongo_indexes
    await init_mongo_indexes()

    print("✅ MongoDB reset complete.\n")


async def main():
    print("\n" + "=" * 50)
    print("  🔄 DATABASE RESET — Wiping all data")
    print("=" * 50 + "\n")

    reset_postgresql()
    await reset_mongodb()

    print("=" * 50)
    print("  ✅ BOTH DATABASES RESET SUCCESSFULLY")
    print("  📦 Ready for fresh data load")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
