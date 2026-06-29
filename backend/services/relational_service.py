"""
============================================================
INF2003 Group 11 — Relational Database Service
Complex SQL queries: RFM segmentation, market basket analysis,
audit trail queries, triggers execution.
============================================================
"""

from typing import List, Dict, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session

from models.relational import (
    Customer, Product, Order, OrderItem, Alert, OrderAuditLog, Outbox,
)


# ============================================================
# RFM SEGMENTATION (Recency, Frequency, Monetary)
# Uses CTEs and NTILE(4) to classify customers.
# ============================================================
def compute_rfm_segmentation(db: Session) -> List[dict]:
    """
    Compute RFM scores and segment labels for all customers.
    Returns list of {customer_id, recency_days, frequency, monetary,
                      r_score, f_score, m_score, segment}
    """
    query = text("""
        WITH order_summary AS (
            SELECT
                o.customer_id,
                MAX(o.order_date) AS last_order_date,
                COUNT(o.order_id) AS frequency,
                COALESCE(SUM(o.total_amount), 0) AS monetary
            FROM orders o
            GROUP BY o.customer_id
        ),
        rfm_scores AS (
            SELECT
                customer_id,
                EXTRACT(DAY FROM (NOW() - last_order_date)) AS recency_days,
                frequency,
                monetary,
                NTILE(4) OVER (ORDER BY EXTRACT(DAY FROM (NOW() - last_order_date)) DESC) AS r_score,
                NTILE(4) OVER (ORDER BY frequency ASC) AS f_score,
                NTILE(4) OVER (ORDER BY monetary ASC) AS m_score
            FROM order_summary
        )
        SELECT
            customer_id::TEXT,
            recency_days,
            frequency,
            ROUND(monetary::numeric, 2) AS monetary,
            r_score,
            f_score,
            m_score,
            (r_score + f_score + m_score) AS total_score,
            CASE
                WHEN (r_score + f_score + m_score) >= 10 THEN 'Champions'
                WHEN (r_score + f_score + m_score) >= 8  THEN 'Loyal Customers'
                WHEN (r_score + f_score + m_score) >= 6  THEN 'Potential Loyalists'
                WHEN (r_score + f_score + m_score) >= 4  THEN 'At Risk'
                ELSE 'Lost'
            END AS segment
        FROM rfm_scores
        ORDER BY total_score DESC;
    """)

    result = db.execute(query)
    rows = result.fetchall()

    return [
        {
            "customer_id": row[0],
            "recency_days": int(row[1]) if row[1] else 0,
            "frequency": int(row[2]),
            "monetary": float(row[3]),
            "r_score": int(row[4]),
            "f_score": int(row[5]),
            "m_score": int(row[6]),
            "total_score": int(row[7]),
            "segment": row[8],
        }
        for row in rows
    ]


# ============================================================
# MARKET BASKET ANALYSIS (Co-occurrence)
# Self-join order_items to find product pairs bought together.
# ============================================================
def compute_market_basket(db: Session, top_n: int = 10) -> List[dict]:
    """
    Find the most common product pairs purchased together.
    Uses a self-join on order_items grouped by order_id.
    """
    query = text("""
        SELECT
            p1.product_id AS product_a,
            pa.name AS name_a,
            p2.product_id AS product_b,
            pb.name AS name_b,
            COUNT(*) AS pair_count
        FROM order_items p1
        JOIN order_items p2
            ON p1.order_id = p2.order_id
            AND p1.product_id < p2.product_id
        JOIN products pa ON pa.product_id = p1.product_id
        JOIN products pb ON pb.product_id = p2.product_id
        GROUP BY p1.product_id, pa.name, p2.product_id, pb.name
        ORDER BY pair_count DESC
        LIMIT :top_n;
    """)

    result = db.execute(query, {"top_n": top_n})
    rows = result.fetchall()

    return [
        {
            "product_a": row[0],
            "name_a": row[1],
            "product_b": row[2],
            "name_b": row[3],
            "pair_count": int(row[4]),
        }
        for row in rows
    ]


# ============================================================
# AUDIT TRAIL QUERY
# Show all changes for a given order from order_audit_log.
# ============================================================
def get_order_audit_trail(db: Session, order_id: str) -> List[dict]:
    """
    Retrieve the full change history for a specific order.
    """
    logs = (
        db.query(OrderAuditLog)
        .filter(OrderAuditLog.order_id == order_id)
        .order_by(OrderAuditLog.changed_at.asc())
        .all()
    )

    return [
        {
            "audit_id": log.audit_id,
            "field_name": log.field_name,
            "old_value": log.old_value,
            "new_value": log.new_value,
            "changed_at": log.changed_at.isoformat() if log.changed_at else None,
        }
        for log in logs
    ]


# ============================================================
# FRAUD ALERTS
# ============================================================
def create_alert(db: Session, customer_id: str, message: str, alert_type: str = "fraud") -> Alert:
    """Insert a fraud/security alert into PostgreSQL."""
    alert = Alert(
        customer_id=customer_id,
        message=message,
        alert_type=alert_type,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_recent_alerts(db: Session, limit: int = 20) -> List[dict]:
    """Get recent alerts for the admin dashboard."""
    alerts = (
        db.query(Alert)
        .order_by(Alert.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "alert_id": a.alert_id,
            "customer_id": str(a.customer_id),
            "message": a.message,
            "alert_type": a.alert_type,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "acknowledged": a.acknowledged,
        }
        for a in alerts
    ]


# ============================================================
# TOP PRODUCTS / CATEGORIES
# ============================================================
def get_top_products(db: Session, limit: int = 10) -> List[dict]:
    """Get top-selling products by total quantity sold."""
    query = text("""
        SELECT
            p.product_id,
            p.name,
            p.category,
            p.unit_price,
            SUM(oi.quantity) AS total_sold,
            SUM(oi.quantity * p.unit_price) AS total_revenue
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        GROUP BY p.product_id, p.name, p.category, p.unit_price
        ORDER BY total_sold DESC
        LIMIT :limit;
    """)

    result = db.execute(query, {"limit": limit})
    rows = result.fetchall()

    return [
        {
            "product_id": row[0],
            "name": row[1],
            "category": row[2],
            "unit_price": float(row[3]),
            "total_sold": int(row[4]),
            "total_revenue": float(row[5]),
        }
        for row in rows
    ]


# ============================================================
# SALES BY CATEGORY
# ============================================================
def get_sales_by_category(db: Session) -> List[dict]:
    """Aggregate sales by product category."""
    query = text("""
        SELECT
            p.category,
            COUNT(DISTINCT oi.order_id) AS order_count,
            SUM(oi.quantity) AS total_units,
            SUM(oi.quantity * p.unit_price) AS total_revenue
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        GROUP BY p.category
        ORDER BY total_revenue DESC;
    """)

    result = db.execute(query)
    rows = result.fetchall()

    return [
        {
            "category": row[0],
            "order_count": int(row[1]),
            "total_units": int(row[2]),
            "total_revenue": float(row[3]),
        }
        for row in rows
    ]
