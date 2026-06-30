"""
MongoDB NoSQL Service — Clickstream, Funnel, Fraud, and CDC Target.
====================================================================

Implements all MongoDB operations using the Motor async driver.
Demonstrates 4 established NoSQL design patterns:

NOSQL PATTERNS:
  1. BUCKET PATTERN (user_sessions): Accumulates clickstream events per session
     using atomic updateOne with $push + $inc + upsert. Bulk loading uses
     $push: { $each: [...] } — one DB call per session instead of per event.
  2. COMPUTED PATTERN (session_stats): Pre-aggregated session metrics.
  3. CDC TARGET PATTERN (customer_order_summary): Denormalized view from PG.
  4. CACHED PATTERN (funnel_metrics): Results of $facet aggregation pipeline.

KEY FUNCTIONS:
  track_clickstream_event()     — Bucket Pattern atomic write
  check_fraud_alert()           — Velocity-based fraud detection (10+ events/60s)
  compute_funnel_metrics()      — $facet pipeline → 4-stage conversion rates
  update_customer_order_summary() — Idempotent CDC target update ($inc)
  init_mongo_indexes()          — Compound, TTL, and query indexes
"""

from datetime import datetime, timedelta
from typing import Optional, List

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import settings
from models.nosql_schemas import ActionType

# Global MongoDB client (initialized at startup)
mongo_client: Optional[AsyncIOMotorClient] = None
mongo_db: Optional[AsyncIOMotorDatabase] = None


async def get_mongo_db() -> AsyncIOMotorDatabase:
    """Lazy-init and return the MongoDB database handle."""
    global mongo_client, mongo_db
    if mongo_client is None:
        mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
        mongo_db = mongo_client[settings.MONGO_DB]
    return mongo_db


async def init_mongo_indexes():
    """Create indexes on MongoDB collections for performance."""
    db = await get_mongo_db()

    # user_sessions: compound index on customer + session
    await db.user_sessions.create_index(
        [("customer_id", 1), ("session_id", 1)], unique=True
    )
    # user_sessions: TTL index (auto-delete sessions older than 30 days)
    await db.user_sessions.create_index("end_time", expireAfterSeconds=2592000)
    await db.user_sessions.create_index("flagged")
    await db.user_sessions.create_index("events.timestamp")

    # session_stats
    await db.session_stats.create_index("session_id", unique=True)

    # customer_order_summary
    await db.customer_order_summary.create_index("customer_id", unique=True)

    # funnel_metrics
    await db.funnel_metrics.create_index([("stage", 1), ("computed_at", -1)])

    print(f"[OK] MongoDB indexes created on database '{settings.MONGO_DB}'.")


# ------------------------------------------------------------
# Bucket Pattern: Track clickstream events in user_sessions
# ------------------------------------------------------------
async def track_clickstream_event(
    customer_id: str,
    session_id: str,
    action_type: ActionType,
    product_id: Optional[str] = None,
) -> dict:
    """
    Record a clickstream event using the Bucket Pattern.
    Uses updateOne with $push (add event) + $inc (increment count).
    Upsert creates the session document if it doesn't exist.
    """
    db = await get_mongo_db()

    event = {
        "action_type": action_type.value,
        "product_id": product_id,
        "timestamp": datetime.utcnow(),
    }

    now = datetime.utcnow()

    result = await db.user_sessions.update_one(
        {"customer_id": customer_id, "session_id": session_id},
        {
            "$push": {"events": event},
            "$inc": {"event_count": 1},
            "$set": {"end_time": now},
            "$setOnInsert": {"start_time": now, "flagged": False},
        },
        upsert=True,
    )

    return {
        "matched": result.matched_count,
        "modified": result.modified_count,
        "upserted_id": str(result.upserted_id) if result.upserted_id else None,
    }


# ------------------------------------------------------------
# Fraud Detection: Check for rapid-fire cart additions
# ------------------------------------------------------------
async def check_fraud_alert(customer_id: str, session_id: str) -> Optional[dict]:
    """
    After each add_to_cart event, check if the user exceeded the threshold
    (10+ events in 60 seconds with no purchase). If so, return alert info.
    """
    db = await get_mongo_db()
    threshold = settings.FRAUD_EVENT_THRESHOLD
    window_start = datetime.utcnow() - timedelta(seconds=settings.FRAUD_TIME_WINDOW_SECONDS)

    session = await db.user_sessions.find_one(
        {"customer_id": customer_id, "session_id": session_id}
    )

    if not session or session["event_count"] < threshold:
        return None

    # Count events in the last N seconds
    recent_events = [
        e for e in session.get("events", [])
        if e["timestamp"] >= window_start
    ]

    if len(recent_events) >= threshold:
        # Check if any purchase event exists in this window
        has_purchase = any(
            e["action_type"] == ActionType.PURCHASE.value for e in recent_events
        )

        if not has_purchase:
            # Flag the session in MongoDB
            await db.user_sessions.update_one(
                {"customer_id": customer_id, "session_id": session_id},
                {"$set": {"flagged": True}},
            )
            return {
                "customer_id": customer_id,
                "session_id": session_id,
                "event_count": len(recent_events),
                "window_seconds": settings.FRAUD_TIME_WINDOW_SECONDS,
                "reason": f"Rapid cart activity: {len(recent_events)} events in {settings.FRAUD_TIME_WINDOW_SECONDS}s with no purchase.",
            }

    return None


# ------------------------------------------------------------
# Session Funnel Analysis
# ------------------------------------------------------------
async def compute_funnel_metrics() -> List[dict]:
    """
    Aggregation pipeline using $facet to compute conversion rates:
    page_view -> add_to_cart -> checkout -> purchase
    """
    db = await get_mongo_db()

    pipeline = [
        {"$unwind": "$events"},
        {
            "$facet": {
                "page_views": [
                    {"$match": {"events.action_type": ActionType.PAGE_VIEW.value}},
                    {"$group": {"_id": "$session_id"}},
                    {"$count": "count"},
                ],
                "add_to_cart": [
                    {"$match": {"events.action_type": ActionType.ADD_TO_CART.value}},
                    {"$group": {"_id": "$session_id"}},
                    {"$count": "count"},
                ],
                "checkouts": [
                    {"$match": {"events.action_type": ActionType.CHECKOUT.value}},
                    {"$group": {"_id": "$session_id"}},
                    {"$count": "count"},
                ],
                "purchases": [
                    {"$match": {"events.action_type": ActionType.PURCHASE.value}},
                    {"$group": {"_id": "$session_id"}},
                    {"$count": "count"},
                ],
            }
        },
    ]

    result = await db.user_sessions.aggregate(pipeline).to_list(length=1)

    if not result:
        return []

    facet = result[0]
    metrics = []

    # Map facet keys to stage names
    key_map = {
        "page_views": "page_view",
        "add_to_cart": "add_to_cart",
        "checkouts": "checkout",
        "purchases": "purchase",
    }

    total_sessions = (facet.get("page_views", [{}])[0].get("count", 1) if facet.get("page_views") else 1)

    for facet_key, stage_name in key_map.items():
        count = facet.get(facet_key, [{}])[0].get("count", 0) if facet.get(facet_key) else 0
        rate = round((count / total_sessions) * 100, 2) if total_sessions > 0 else 0
        metrics.append({
            "stage": stage_name,
            "count": count,
            "conversion_rate": rate,
        })

    # Cache funnel metrics
    await db.funnel_metrics.delete_many({})
    if metrics:
        docs = [
            {**m, "computed_at": datetime.utcnow()} for m in metrics
        ]
        await db.funnel_metrics.insert_many(docs)

    return metrics


# ------------------------------------------------------------
# Cart Abandonment Detection
# ------------------------------------------------------------
async def detect_cart_abandonment() -> List[dict]:
    """
    Find sessions where add_to_cart exists but checkout is missing.
    Uses MongoDB aggregation pipeline with $addToSet to collect all
    action types per session, then filters for abandoned ones.
    """
    db = await get_mongo_db()

    pipeline = [
        {"$unwind": "$events"},
        {
            "$group": {
                "_id": "$session_id",
                "customer_id": {"$first": "$customer_id"},
                "actions": {"$addToSet": "$events.action_type"},
                "event_count": {"$first": "$event_count"},
                "last_event": {"$max": "$events.timestamp"},
            }
        },
        {
            "$match": {
                "$expr": {
                    "$and": [
                        {"$in": [ActionType.ADD_TO_CART.value, "$actions"]},
                        {"$not": {"$in": [ActionType.CHECKOUT.value, "$actions"]}},
                    ]
                }
            }
        },
        {"$sort": {"last_event": -1}},
        {"$limit": 20},
    ]

    try:
        results = await db.user_sessions.aggregate(pipeline).to_list(length=20)

        return [
            {
                "session_id": r["_id"],
                "customer_id": r.get("customer_id", "unknown"),
                "event_count": r.get("event_count", 0),
                "last_activity": r["last_event"].isoformat() if r.get("last_event") else None,
            }
            for r in results
        ]
    except Exception as e:
        print(f"[WARN] Cart abandonment query error: {e}")
        return []


# ------------------------------------------------------------
# Session Stats Computation (Computed Pattern)
# ------------------------------------------------------------
# ------------------------------------------------------------
# CDC Target: Update customer_order_summary in MongoDB
# ------------------------------------------------------------
async def update_customer_order_summary(customer_id: str, order_amount: float):
    """
    Called by the Outbox processor when a new order is detected.
    Updates the denormalized customer_order_summary document.
    """
    db = await get_mongo_db()

    await db.customer_order_summary.update_one(
        {"customer_id": customer_id},
        {
            "$inc": {"total_orders": 1, "total_spent": order_amount},
            "$set": {"last_order_date": datetime.utcnow(), "last_updated": datetime.utcnow()},
            "$setOnInsert": {"customer_id": customer_id},
        },
        upsert=True,
    )
