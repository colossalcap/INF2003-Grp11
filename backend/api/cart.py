"""
============================================================
INF2003 Group 11 — Cart & Clickstream API
Tracks user actions in MongoDB (Bucket Pattern).
Includes fraud detection logic.
============================================================
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.relational import get_db, User
from models.nosql_schemas import ActionType
from api.auth import get_current_user
from services.nosql_service import track_clickstream_event, check_fraud_alert
from services.relational_service import create_alert

router = APIRouter()


class ClickstreamPayload(BaseModel):
    action_type: str  # page_view, add_to_cart, checkout, purchase
    product_id: Optional[str] = None
    session_id: Optional[str] = None


@router.post("/event")
async def record_clickstream_event(
    payload: ClickstreamPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Record a clickstream event in MongoDB using the Bucket Pattern.
    After add_to_cart events, performs fraud detection check.
    """
    # Map action type string to enum
    try:
        action_type = ActionType(payload.action_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action_type. Must be one of: {[a.value for a in ActionType]}",
        )

    # Generate session ID if not provided
    session_id = payload.session_id or str(uuid.uuid4())
    customer_id = str(current_user.user_id)

    # Track in MongoDB (Bucket Pattern)
    result = await track_clickstream_event(
        customer_id=customer_id,
        session_id=session_id,
        action_type=action_type,
        product_id=payload.product_id,
    )

    # Fraud detection: check after add_to_cart
    fraud_alert = None
    if action_type == ActionType.ADD_TO_CART:
        fraud_alert = await check_fraud_alert(customer_id, session_id)

    if fraud_alert:
        # Persist alert to PostgreSQL
        create_alert(
            db=db,
            customer_id=customer_id,
            message=f"Fraud Alert: {fraud_alert['reason']}",
            alert_type="fraud",
        )

    return {
        "status": "recorded",
        "session_id": session_id,
        "action_type": action_type.value,
        "fraud_alert": fraud_alert,
        "mongo_result": result,
    }


@router.get("/session/{session_id}")
async def get_session_events(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get all events for a specific session from MongoDB."""
    from services.nosql_service import get_mongo_db

    db = await get_mongo_db()
    session = await db.user_sessions.find_one(
        {"session_id": session_id, "customer_id": str(current_user.user_id)}
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Convert ObjectId to string
    session["_id"] = str(session["_id"])
    # Convert datetime objects to ISO strings
    if "start_time" in session:
        session["start_time"] = session["start_time"].isoformat()
    if "end_time" in session:
        session["end_time"] = session["end_time"].isoformat()
    for event in session.get("events", []):
        if "timestamp" in event:
            event["timestamp"] = event["timestamp"].isoformat()

    return session
