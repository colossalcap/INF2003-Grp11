"""
============================================================
INF2003 Group 11 — Pydantic Models for MongoDB Documents
Defines the document structures for NoSQL collections.
============================================================
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field


# ------------------------------------------------------------
# Clickstream Event Types
# ------------------------------------------------------------
class ActionType(str, Enum):
    PAGE_VIEW = "page_view"
    ADD_TO_CART = "add_to_cart"
    CHECKOUT = "checkout"
    PURCHASE = "purchase"


# ------------------------------------------------------------
# Individual Clickstream Event
# ------------------------------------------------------------
class ClickstreamEvent(BaseModel):
    action_type: ActionType
    product_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ------------------------------------------------------------
# User Session Document (Bucket Pattern)
# ------------------------------------------------------------
class UserSession(BaseModel):
    """
    MongoDB document structure for user_sessions collection.
    Uses the Bucket Pattern: accumulates events in the 'events' array,
    incrementing 'event_count' per action.
    """
    customer_id: str
    session_id: str
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: datetime = Field(default_factory=datetime.utcnow)
    event_count: int = 0
    events: List[ClickstreamEvent] = []
    flagged: bool = False  # Set by fraud detection


# ------------------------------------------------------------
# Session Stats Document (Computed Pattern)
# ------------------------------------------------------------
class SessionStats(BaseModel):
    """
    Pre-aggregated summary per session.
    Updated via Change Streams or post-processing.
    """
    session_id: str
    customer_id: Optional[str] = None
    total_events: int = 0
    unique_products_viewed: int = 0
    cart_additions: int = 0
    checkout_reached: bool = False
    purchase_completed: bool = False
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# ------------------------------------------------------------
# Customer Order Summary (CDC target from Outbox)
# ------------------------------------------------------------
class CustomerOrderSummary(BaseModel):
    """
    Denormalized view of customer orders, synced from PostgreSQL
    via the Outbox Pattern / CDC.
    """
    customer_id: str
    total_orders: int = 0
    total_spent: float = 0.0
    last_order_date: Optional[datetime] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# ------------------------------------------------------------
# Funnel Metrics (aggregated conversion rates)
# ------------------------------------------------------------
class FunnelMetrics(BaseModel):
    """
    Cached funnel conversion metrics for the admin dashboard.
    """
    stage: str
    count: int
    conversion_rate: Optional[float] = None
    computed_at: datetime = Field(default_factory=datetime.utcnow)
