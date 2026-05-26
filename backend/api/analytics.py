"""
============================================================
INF2003 Group 11 — Analytics API
RFM segmentation, market basket, funnel analysis,
fraud alerts, and audit trail.
============================================================
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from models.relational import get_db, User
from api.auth import get_current_user, get_admin_user
from services.relational_service import (
    compute_rfm_segmentation,
    compute_market_basket,
    get_order_audit_trail,
    get_recent_alerts,
    get_top_products,
    get_sales_by_category,
)
from services.nosql_service import compute_funnel_metrics, detect_cart_abandonment

router = APIRouter()


@router.get("/rfm")
async def get_rfm_segmentation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Compute RFM (Recency, Frequency, Monetary) segmentation.
    Uses SQL CTEs and NTILE(4) to classify customers into:
    Champions, Loyal Customers, Potential Loyalists, At Risk, Lost.
    """
    results = compute_rfm_segmentation(db)
    return {"segments": results, "total_customers": len(results)}


@router.get("/market-basket")
async def get_market_basket(
    top_n: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Market Basket Analysis: Find the most common product pairs
    purchased together using self-join on order_items.
    """
    results = compute_market_basket(db, top_n=top_n)
    return {"pairs": results, "total_pairs": len(results)}


@router.get("/funnel")
async def get_funnel_metrics(
    current_user: User = Depends(get_current_user),
):
    """
    Session Funnel Analysis from MongoDB:
    Computes conversion rates across the funnel:
    page_view -> add_to_cart -> checkout -> purchase.
    Uses MongoDB aggregation pipeline with $facet.
    """
    metrics = await compute_funnel_metrics()
    return {"funnel": metrics}


@router.get("/cart-abandonment")
async def get_cart_abandonment(
    current_user: User = Depends(get_current_user),
):
    """
    Detect sessions where add_to_cart exists but checkout is missing.
    Returns list of abandoned sessions from MongoDB.
    """
    results = await detect_cart_abandonment()
    return {"abandoned_sessions": results, "count": len(results)}


@router.get("/audit/{order_id}")
async def get_audit_trail(
    order_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve the full audit trail for a specific order.
    Shows all field changes logged by the audit trigger.
    """
    results = get_order_audit_trail(db, order_id)
    return {"order_id": order_id, "changes": results, "total_changes": len(results)}


@router.get("/alerts")
async def get_alerts(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Get recent fraud and security alerts (admin only).
    """
    results = get_recent_alerts(db, limit=limit)
    return {"alerts": results, "count": len(results)}


@router.get("/top-products")
async def get_top_products_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50),
):
    """Get top-selling products by quantity sold."""
    results = get_top_products(db, limit=limit)
    return {"products": results}


@router.get("/sales-by-category")
async def get_sales_by_category_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Aggregate sales by product category."""
    results = get_sales_by_category(db)
    return {"categories": results}
