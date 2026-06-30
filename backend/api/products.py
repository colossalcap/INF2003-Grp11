"""
============================================================
INF2003 Group 11 — Products API
Product catalog endpoints (PostgreSQL).
============================================================
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.relational import get_db, Product

router = APIRouter()


@router.get("/")
async def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by product ID"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List products with optional category filter and pagination."""
    query = db.query(Product)

    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    if search:
        query = query.filter(
            or_(
                Product.product_id.ilike(f"%{search}%"),
                Product.name.ilike(f"%{search}%")
            )
        )

    total = query.count()
    products = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "products": [
            {
                "product_id": p.product_id,
                "name": p.name,
                "category": p.category,
                "unit_price": p.unit_price,
                "stock_quantity": p.stock_quantity,
            }
            for p in products
        ],
    }


@router.get("/{product_id}")
async def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get details for a single product."""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    return {
        "product_id": product.product_id,
        "name": product.name,
        "category": product.category,
        "unit_price": product.unit_price,
        "stock_quantity": product.stock_quantity,
    }


@router.get("/categories/all")
async def list_categories(db: Session = Depends(get_db)):
    """Get distinct product categories."""
    categories = (
        db.query(Product.category)
        .distinct()
        .order_by(Product.category)
        .all()
    )
    return {"categories": [c[0] for c in categories]}
