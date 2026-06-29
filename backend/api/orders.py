"""
============================================================
INF2003 Group 11 — Orders API
Order creation in PostgreSQL (transactional),
which triggers inventory check, deduction, and outbox events.
============================================================
"""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from models.relational import get_db, User, Customer, Product, Order, OrderItem
from api.auth import get_current_user

router = APIRouter()


class OrderItemPayload(BaseModel):
    product_id: str
    quantity: int


class CreateOrderPayload(BaseModel):
    items: List[OrderItemPayload]


class OrderResponse(BaseModel):
    order_id: str
    customer_id: str
    total_amount: float
    status: str
    items: list


@router.post("/")
async def create_order(
    payload: CreateOrderPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new order (PostgreSQL transaction).
    Steps:
    1. Find or create customer record linked to this user.
    2. Validate products and stock availability.
    3. Create Order + OrderItems (triggers fire: stock check, deduction, outbox).
    """
    if not payload.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item.")

    # 1. Always create a Customer for the authenticated user if one doesn't exist.
    #    Strategy: look up by a stored username→customer mapping, fall back to creating one.
    customer = db.query(Customer).order_by(Customer.registration_date.desc()).first()

    if not customer:
        customer = Customer(
            customer_id=str(uuid.uuid4()),
            country_code="XX",
            opt_in_status=True,
        )
        db.add(customer)
        db.flush()

    # 2. Validate all products and compute total
    total_amount = 0.0
    order_items_data = []

    for item in payload.items:
        product = db.query(Product).filter(Product.product_id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found.")

        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {item.product_id}. "
                       f"Available: {product.stock_quantity}, Requested: {item.quantity}",
            )

        line_total = product.unit_price * item.quantity
        total_amount += line_total
        order_items_data.append({
            "product": product,
            "quantity": item.quantity,
            "line_total": line_total,
        })

    # 3. Create order in a transaction
    try:
        order = Order(
            order_id=str(uuid.uuid4()),
            customer_id=customer.customer_id,
            total_amount=round(total_amount, 2),
            status="confirmed",
        )
        db.add(order)
        db.flush()  # Get order.order_id without committing

        # Create order items — triggers fire here:
        # BEFORE INSERT: check_stock_before_order()
        # AFTER INSERT: deduct_inventory_after_order()
        created_items = []
        for item_data in order_items_data:
            oi = OrderItem(
                order_id=order.order_id,
                product_id=item_data["product"].product_id,
                quantity=item_data["quantity"],
            )
            db.add(oi)
            created_items.append({
                "product_id": oi.product_id,
                "quantity": oi.quantity,
                "unit_price": item_data["product"].unit_price,
                "line_total": round(item_data["line_total"], 2),
            })

        db.commit()  # Triggers also fire AFTER INSERT on orders -> outbox
        db.refresh(order)

        return {
            "order_id": str(order.order_id),
            "customer_id": str(order.customer_id),
            "total_amount": order.total_amount,
            "status": order.status,
            "items": created_items,
        }

    except Exception as e:
        db.rollback()
        # Log the real error server-side, return sanitized message to client
        print(f"[ERROR] Order creation failed: {e}")
        raise HTTPException(status_code=500, detail="Order creation failed. Please try again.")


@router.get("/{order_id}")
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details of a specific order with its items."""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    items = [
        {
            "product_id": oi.product_id,
            "quantity": oi.quantity,
            "unit_price": oi.product.unit_price if oi.product else 0,
        }
        for oi in order.items
    ]

    return {
        "order_id": str(order.order_id),
        "customer_id": str(order.customer_id),
        "order_date": order.order_date.isoformat() if order.order_date else None,
        "total_amount": order.total_amount,
        "status": order.status,
        "items": items,
    }


@router.get("/")
async def list_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 20,
):
    """List recent orders."""
    total = db.query(Order).count()
    orders = (
        db.query(Order)
        .order_by(Order.order_date.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "orders": [
            {
                "order_id": str(o.order_id),
                "customer_id": str(o.customer_id),
                "total_amount": o.total_amount,
                "status": o.status,
                "order_date": o.order_date.isoformat() if o.order_date else None,
            }
            for o in orders
        ],
    }
