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
