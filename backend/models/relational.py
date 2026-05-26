"""
============================================================
INF2003 Group 11 — SQLAlchemy ORM Models (PostgreSQL)
Tables: customers, products, orders, order_items, outbox,
        alerts, order_audit_log, users
============================================================
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text,
    ForeignKey, CheckConstraint,
    create_engine,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from config import settings

Base = declarative_base()

# Engine and session factory
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# ------------------------------------------------------------
# Users (for JWT authentication)
# ------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100))
    role = Column(String(20), default="customer")  # customer, admin
    created_at = Column(DateTime, default=datetime.utcnow)


# ------------------------------------------------------------
# Customers
# ------------------------------------------------------------
class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    registration_date = Column(DateTime, default=datetime.utcnow)
    country_code = Column(String(3))
    opt_in_status = Column(Boolean, default=True)

    # Relationships
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")


# ------------------------------------------------------------
# Products
# ------------------------------------------------------------
class Product(Base):
    __tablename__ = "products"

    product_id = Column(String(50), primary_key=True)
    category = Column(String(100), nullable=False, index=True)
    unit_price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("stock_quantity >= 0", name="ck_stock_non_negative"),
    )

    # Relationships
    order_items = relationship("OrderItem", back_populates="product")


# ------------------------------------------------------------
# Orders
# ------------------------------------------------------------
class Order(Base):
    __tablename__ = "orders"

    order_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.customer_id"), nullable=False, index=True)
    order_date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, default=0.0)
    status = Column(String(20), default="pending")  # pending, confirmed, shipped, cancelled

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


# ------------------------------------------------------------
# Order Items
# ------------------------------------------------------------
class OrderItem(Base):
    __tablename__ = "order_items"

    item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(50), ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_quantity_positive"),
    )

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


# ------------------------------------------------------------
# Outbox Table (for Outbox Pattern / CDC)
# ------------------------------------------------------------
class Outbox(Base):
    __tablename__ = "outbox"

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    aggregate_id = Column(String(255), nullable=False)
    event_type = Column(String(100), nullable=False, index=True)
    payload = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False, index=True)


# ------------------------------------------------------------
# Alerts (Fraud Detection)
# ------------------------------------------------------------
class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    message = Column(Text, nullable=False)
    alert_type = Column(String(50), default="fraud")
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged = Column(Boolean, default=False)


# ------------------------------------------------------------
# Order Audit Log (for Audit Trigger)
# ------------------------------------------------------------
class OrderAuditLog(Base):
    __tablename__ = "order_audit_log"

    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    changed_by = Column(String(50))
    field_name = Column(String(100))
    old_value = Column(Text)
    new_value = Column(Text)
    changed_at = Column(DateTime, default=datetime.utcnow)


# ------------------------------------------------------------
# Helper: Get DB Session
# ------------------------------------------------------------
def get_db():
    """Yield a database session, ensuring it's closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
