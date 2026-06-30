"""
============================================================
INF2003 Group 11 — Data Loader
Ingests CSV files into PostgreSQL and MongoDB.
Reads from data/ directory.

Performance: Set DEMO_MODE=True for lecturer demos (~1-2 min).
             Set DEMO_MODE=False for full dataset (~20 min).
============================================================
"""

import re
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from collections import defaultdict

import pandas as pd

from models.relational import (
    SessionLocal, engine, Base, Customer, Product, Order, OrderItem, User,
)
from models.nosql_schemas import ActionType
from services.nosql_service import get_mongo_db

# ============================================================
# CONFIGURATION — Toggle demo mode for fast lecturer setup
# ============================================================
DEMO_MODE = True  # Set to False to load the full 275K+ row dataset

# Row limits in demo mode (full dataset if DEMO_MODE=False)
DEMO_CUSTOMERS = 2000       # Full: 20,000
DEMO_PRODUCTS = None        # Full: 1,197 (always load all — tiny)
DEMO_ORDERS = 3000          # Full: 33,580
DEMO_CLICKSTREAM_EVENTS = 40000  # Full: 760,958
DEMO_SESSIONS = 10000       # Full: 120,000

def _nrows(demo_limit):
    """Return nrows for pd.read_csv based on DEMO_MODE."""
    return demo_limit if DEMO_MODE else None

# Resolve data directory: backend/data_loader.py -> project_root/data/
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# ============================================================
# PostgreSQL Loader
# ============================================================
def load_customers_postgres(batch_size: int = 1000):
    """Load customers.csv into PostgreSQL."""
    filepath = DATA_DIR / "customers.csv"
    if not filepath.exists():
        print(f"[WARN] {filepath} not found. Skipping customers.", flush=True)
        return 0

    df = pd.read_csv(filepath, nrows=_nrows(DEMO_CUSTOMERS))
    db = SessionLocal()
    count = 0

    # Pre-compute the shared password hash (bcrypt is slow, do once!)
    from passlib.context import CryptContext
    pwd_ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')
    SHARED_PASSWORD_HASH = pwd_ctx.hash('password123')

    try:
        for _, row in df.iterrows():
            customer = Customer(
                customer_id=str(uuid.uuid4()),
                country_code=str(row.get("country", "XX"))[:3],
                opt_in_status=str(row.get("marketing_opt_in", "True")).lower() == "true",
            )
            db.add(customer)

            # Also create a User for authentication (using customer_id as mapping)
            csv_id = int(row['customer_id'])
            if not db.query(User).filter_by(username=f"user_{csv_id}").first():
                user = User(
                    username=f"user_{csv_id}",
                    email=str(row.get("email", f"user{csv_id}@example.com")),
                    password_hash=SHARED_PASSWORD_HASH,
                    display_name=str(row.get("name", f"User {csv_id}")),
                    role="admin" if csv_id == 1 else "customer",
                )
                db.add(user)

            count += 1
            if count % batch_size == 0:
                db.commit()
                print(f"  Loaded {count} customers...", flush=True)

        db.commit()
        print(f"[OK] Loaded {count} customers into PostgreSQL.", flush=True)
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error loading customers: {e}", flush=True)
        raise
    finally:
        db.close()

    return count


def load_products_postgres(batch_size: int = 1000):
    """Load products.csv into PostgreSQL."""
    filepath = DATA_DIR / "products.csv"
    if not filepath.exists():
        print(f"[WARN] {filepath} not found. Skipping products.", flush=True)
        return 0

    df = pd.read_csv(filepath, nrows=_nrows(DEMO_PRODUCTS))
    db = SessionLocal()
    count = 0

    try:
        for _, row in df.iterrows():
            existing = db.query(Product).filter_by(product_id=str(row["product_id"])).first()
            if existing:
                continue

            raw_name = str(row.get("name", f"Product {row['product_id']}"))
            # Strip trailing number (e.g. "SSD MediumBlue 149" → "SSD MediumBlue")
            clean_name = re.sub(r'\s+\d+$', '', raw_name)

            product = Product(
                product_id=str(row["product_id"]),
                name=clean_name,
                category=str(row.get("category", "Uncategorized")),
                unit_price=float(row.get("price_usd", 0)),
                stock_quantity=1000,  # Default stock
            )
            db.add(product)
            count += 1

            if count % batch_size == 0:
                db.commit()
                print(f"  Loaded {count} products...", flush=True)

        db.commit()
        print(f"[OK] Loaded {count} products into PostgreSQL.", flush=True)
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error loading products: {e}", flush=True)
        raise
    finally:
        db.close()

    return count


def load_orders_postgres(batch_size: int = 500):
    """Load orders.csv and order_items.csv into PostgreSQL."""
    orders_path = DATA_DIR / "orders.csv"
    items_path = DATA_DIR / "order_items.csv"

    if not orders_path.exists():
        print(f"[WARN] {orders_path} not found. Skipping orders.", flush=True)
        return 0

    df_orders = pd.read_csv(orders_path, nrows=_nrows(DEMO_ORDERS))
    df_items = pd.read_csv(items_path) if items_path.exists() else None
    # If we sampled orders, filter items to only those orders
    if DEMO_MODE and df_items is not None:
        valid_order_ids = set(df_orders["order_id"].astype(str))
        df_items = df_items[df_items["order_id"].astype(str).isin(valid_order_ids)]

    db = SessionLocal()
    count = 0

    # Pre-compute shared password hash
    from passlib.context import CryptContext
    pwd_ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')
    SHARED_HASH = pwd_ctx.hash('password123')

    try:
        # Map each CSV customer_id to a unique PostgreSQL UUID customer
        csv_customer_ids = df_orders["customer_id"].unique()
        existing_customers = {}

        for cid in csv_customer_ids:
            int_cid = int(cid)
            # Create a unique customer per CSV customer_id
            new_cust = Customer(
                customer_id=str(uuid.uuid4()),
                country_code="XX",
                opt_in_status=True,
            )
            db.add(new_cust)
            db.flush()
            existing_customers[int_cid] = new_cust.customer_id

            # Also create a User record so these customers can log in via JWT
            existing_user = db.query(User).filter_by(username=f"user_{int_cid}").first()
            if not existing_user:
                user = User(
                    username=f"user_{int_cid}",
                    email=f"user{int_cid}@ecommerce.local",
                    password_hash=SHARED_HASH,
                    display_name=f"Customer {int_cid}",
                    role="admin" if int_cid == 1 else "customer",
                )
                db.add(user)

        db.commit()

        # Load orders
        for _, row in df_orders.iterrows():
            csv_cid = int(row["customer_id"])
            cust_uuid = existing_customers.get(csv_cid)
            if not cust_uuid:
                continue

            order = Order(
                order_id=str(uuid.uuid4()),
                customer_id=cust_uuid,
                order_date=pd.to_datetime(row["order_time"]),
                total_amount=float(row.get("total_usd", 0)),
                status="confirmed",
            )
            db.add(order)
            db.flush()

            # Load order items for this order
            if df_items is not None:
                order_items = df_items[df_items["order_id"] == row["order_id"]]
                for _, item_row in order_items.iterrows():
                    # Check product exists
                    product = db.query(Product).filter_by(
                        product_id=str(int(item_row["product_id"]))
                    ).first()
                    if product and product.stock_quantity >= int(item_row.get("quantity", 1)):
                        oi = OrderItem(
                            order_id=order.order_id,
                            product_id=product.product_id,
                            quantity=int(item_row.get("quantity", 1)),
                        )
                        db.add(oi)
                        # Manually deduct stock (trigger handles this in prod)
                        product.stock_quantity -= int(item_row.get("quantity", 1))

            count += 1
            if count % batch_size == 0:
                db.commit()
                print(f"  Loaded {count} orders...", flush=True)

        db.commit()
        print(f"[OK] Loaded {count} orders into PostgreSQL.", flush=True)
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error loading orders: {e}", flush=True)
        raise
    finally:
        db.close()

    return count


# ============================================================
# MongoDB Loader (BATCH-OPTIMIZED)
# ============================================================
async def load_clickstream_to_mongo(batch_size: int = 5000):
    """
    Load clickstream events from events.csv and sessions.csv into MongoDB.
    Uses the Bucket Pattern (user_sessions collection).

    OPTIMIZED: Uses $push with $each to batch all events per session
    into a SINGLE MongoDB operation, instead of one call per event.
    Sessions are bulk-inserted with insert_many (unordered, ignore dupes).
    """
    events_path = DATA_DIR / "clickstream_events.csv"
    sessions_path = DATA_DIR / "sessions.csv"

    if not events_path.exists() and not sessions_path.exists():
        print("[WARN] No clickstream files found. Skipping MongoDB load.", flush=True)
        return 0

    db = await get_mongo_db()
    total_count = 0

    # ----------------------------------------------------------
    # Phase 1: Bulk-insert session documents
    # ----------------------------------------------------------
    if sessions_path.exists():
        df_sessions = pd.read_csv(sessions_path, nrows=_nrows(DEMO_SESSIONS))
        session_docs = []
        seen = set()

        for _, row in df_sessions.iterrows():
            sid = str(row["session_id"])
            cid = str(row["customer_id"])
            key = (cid, sid)
            if key in seen:
                continue
            seen.add(key)
            now = datetime.utcnow()
            session_docs.append({
                "customer_id": cid,
                "session_id": sid,
                "events": [],
                "event_count": 0,
                "start_time": now,
                "end_time": now,
                "flagged": False,
            })

        if session_docs:
            try:
                result = await db.user_sessions.insert_many(session_docs, ordered=False)
                total_count += len(result.inserted_ids)
                print(f"  Bulk-inserted {len(result.inserted_ids)} session documents.", flush=True)
            except Exception:
                # Duplicate key errors are fine — sessions may already exist
                print("  Sessions exist, skipping bulk insert.", flush=True)

    # ----------------------------------------------------------
    # Phase 2: Batch-load events grouped by session
    # ----------------------------------------------------------
    if events_path.exists():
        print("  Reading clickstream events...", flush=True)
        df_events = pd.read_csv(events_path, nrows=_nrows(DEMO_CLICKSTREAM_EVENTS))
        print(f"  Grouping {len(df_events)} events by session...", flush=True)

        # Map CSV event types to ActionType
        type_map = {
            "page_view": ActionType.PAGE_VIEW.value,
            "add_to_cart": ActionType.ADD_TO_CART.value,
            "checkout": ActionType.CHECKOUT.value,
            "purchase": ActionType.PURCHASE.value,
            "remove_from_cart": ActionType.PAGE_VIEW.value,
        }

        # Group events by (customer_id, session_id) in memory
        session_events: dict = defaultdict(list)
        session_customer: dict = {}  # session_id -> customer_id

        for _, row in df_events.iterrows():
            event_type_str = str(row.get("event_type", "page_view")).lower()
            action_type = type_map.get(event_type_str, ActionType.PAGE_VIEW.value)
            product_id = str(int(row["product_id"])) if pd.notna(row.get("product_id")) else None
            session_id = str(row["session_id"])
            customer_id = "unknown"

            session_events[session_id].append({
                "action_type": action_type,
                "product_id": product_id,
                "timestamp": datetime.utcnow(),
            })
            session_customer[session_id] = customer_id

        # Batch-write: one update_one per session with $push + $each
        event_count = 0
        ops_count = 0
        sessions_processed = 0

        for session_id, events in session_events.items():
            customer_id = session_customer.get(session_id, "unknown")
            n = len(events)

            await db.user_sessions.update_one(
                {"customer_id": customer_id, "session_id": session_id},
                {
                    "$push": {"events": {"$each": events}},
                    "$inc": {"event_count": n},
                    "$set": {"end_time": datetime.utcnow()},
                    "$setOnInsert": {"start_time": datetime.utcnow(), "flagged": False},
                },
                upsert=True,
            )

            event_count += n
            ops_count += 1
            sessions_processed += 1

            if sessions_processed % batch_size == 0:
                print(f"  Batched {event_count} events across {sessions_processed} sessions...", flush=True)

        print(f"[OK] Loaded {event_count} clickstream events across {sessions_processed} sessions.", flush=True)
        total_count += event_count

    return total_count


# ============================================================
# Main Loader
# ============================================================
def run_data_loader():
    """Run the full data ingestion pipeline."""
    mode_str = "DEMO MODE (fast)" if DEMO_MODE else "FULL DATASET (slow)"
    print("=" * 60, flush=True)
    print(f"[DATA LOADER] E-Commerce Data Loader — {mode_str}", flush=True)
    print("=" * 60, flush=True)

    # Ensure PostgreSQL tables exist before loading
    print("\n--- Initializing PostgreSQL tables ---", flush=True)
    Base.metadata.create_all(bind=engine)
    print("[OK] Tables ensured.", flush=True)

    print("\n--- PostgreSQL: Customers ---", flush=True)
    load_customers_postgres()

    print("\n--- PostgreSQL: Products ---", flush=True)
    load_products_postgres()

    print("\n--- PostgreSQL: Orders & Order Items ---", flush=True)
    load_orders_postgres()

    print("\n--- MongoDB: Clickstream Events ---", flush=True)
    asyncio.run(load_clickstream_to_mongo())

    print("\n" + "=" * 60, flush=True)
    print("[OK] Data loading complete!", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    run_data_loader()
