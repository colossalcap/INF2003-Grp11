"""
============================================================
INF2003 Group 11 — Sync Service (CDC / Outbox Pattern)
Polls the PostgreSQL outbox table for unpublished events
and synchronizes data to MongoDB (customer_order_summary).
============================================================
"""

import asyncio
import json
from datetime import datetime
from typing import Optional

from sqlalchemy import text

from config import settings
from models.relational import SessionLocal, Outbox
from services.nosql_service import update_customer_order_summary

# Background task reference
_outbox_task: Optional[asyncio.Task] = None


async def start_outbox_processor():
    """
    Start the background outbox processing task.
    Polls the outbox table every N seconds for unprocessed events.
    """
    global _outbox_task
    if _outbox_task is not None:
        return

    _outbox_task = asyncio.create_task(_process_outbox_loop())
    print(f"📬 Outbox processor started (poll interval: {settings.OUTBOX_POLL_INTERVAL_SECONDS}s).")


async def stop_outbox_processor():
    """Gracefully stop the outbox processor."""
    global _outbox_task
    if _outbox_task is not None:
        _outbox_task.cancel()
        try:
            await _outbox_task
        except asyncio.CancelledError:
            pass
        _outbox_task = None


async def _process_outbox_loop():
    """
    Infinite loop: poll the outbox table, process unprocessed events,
    mark them as processed, then sleep.
    """
    while True:
        try:
            await process_outbox_batch()
        except Exception as e:
            print(f"⚠️ Outbox processor error: {e}")
        await asyncio.sleep(settings.OUTBOX_POLL_INTERVAL_SECONDS)


async def process_outbox_batch(batch_size: int = 50):
    """
    Fetch and process a batch of unprocessed outbox events.
    For each 'order_created' event, update the customer_order_summary
    in MongoDB to demonstrate CDC synchronization.
    """
    db = SessionLocal()
    try:
        # Fetch unprocessed events
        events = (
            db.query(Outbox)
            .filter(Outbox.processed == False)
            .order_by(Outbox.created_at.asc())
            .limit(batch_size)
            .all()
        )

        for event in events:
            await _handle_outbox_event(event)

            # Mark as processed
            event.processed = True

        db.commit()

        if events:
            print(f"📬 Processed {len(events)} outbox events.")

    finally:
        db.close()


async def _handle_outbox_event(event: Outbox):
    """
    Handle a single outbox event based on its type.
    - order_created: Update customer_order_summary in MongoDB.
    """
    payload = event.payload

    if event.event_type == "order_created":
        customer_id = payload.get("customer_id")
        total_amount = float(payload.get("total_amount", 0))

        if customer_id:
            await update_customer_order_summary(
                customer_id=str(customer_id),
                order_amount=total_amount,
            )
            print(f"  ✅ Synced order to MongoDB for customer {customer_id}")

    # Additional event types can be handled here:
    # elif event.event_type == "order_cancelled": ...
