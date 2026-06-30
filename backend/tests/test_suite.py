"""
============================================================
INF2003 Group 11 — Comprehensive API Test Suite
Tests every endpoint, trigger, error case, and DB operation.
Run with: docker exec -it ecommerce-backend python tests/test_suite.py
============================================================
"""

import sys
import os
import time
import uuid
from datetime import datetime

# Ensure /app is in the Python path for project module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx

# ── Configuration ───────────────────────────────────────────
BASE_URL = "http://localhost:8000"
PASS = 0
FAIL = 0
ERRORS = []


def log(level: str, msg: str):
    """Print formatted test output."""
    icon = {"PASS": "✅", "FAIL": "❌", "INFO": "ℹ️", "HEADER": "📋"}
    print(f"  {icon.get(level, '•')} {msg}")


def assert_eq(actual, expected, label: str) -> bool:
    """Assert equality and track pass/fail."""
    global PASS, FAIL
    if actual == expected:
        PASS += 1
        log("PASS", label)
        return True
    else:
        FAIL += 1
        msg = f"{label} — expected {expected!r}, got {actual!r}"
        ERRORS.append(msg)
        log("FAIL", msg)
        return False


def assert_status(resp, code: int, label: str) -> bool:
    return assert_eq(resp.status_code, code, f"{label} [HTTP {code}]")


def assert_contains(data, key, label: str) -> bool:
    global PASS, FAIL
    if key in data:
        PASS += 1
        log("PASS", label)
        return True
    FAIL += 1
    msg = f"{label} — key '{key}' not found in response"
    ERRORS.append(msg)
    log("FAIL", msg)
    return False


def assert_gt(actual, minimum, label: str) -> bool:
    global PASS, FAIL
    if actual > minimum:
        PASS += 1
        log("PASS", label)
        return True
    FAIL += 1
    msg = f"{label} — expected > {minimum}, got {actual}"
    ERRORS.append(msg)
    log("FAIL", msg)
    return False


def section(title: str):
    print(f"\n{'═'*60}")
    print(f"  {title}")
    print(f"{'═'*60}")


# ── HTTP Clients ────────────────────────────────────────────
client = httpx.Client(timeout=30)
auth_client = httpx.Client(timeout=30)
admin_client = httpx.Client(timeout=30)


def setup():
    """Create test users and obtain auth tokens."""
    global PASS, FAIL

    unique = str(uuid.uuid4())[:8]
    test_user = f"tester_{unique}"
    test_email = f"tester_{unique}@test.com"
    test_pass = "testpass123"

    section("SETUP — Register & Authenticate")

    # 1. Register regular user
    resp = client.post(f"{BASE_URL}/api/auth/register", json={
        "username": test_user,
        "email": test_email,
        "password": test_pass,
        "display_name": "Test User"
    })
    assert_status(resp, 200, "Register regular user")
    data = resp.json()
    assert_contains(data, "access_token", "Register returns access_token")
    regular_token = data["access_token"]
    auth_client.headers["Authorization"] = f"Bearer {regular_token}"

    # 2. Register admin user
    admin_name = f"admin_{unique}"
    admin_email = f"admin_{unique}@test.com"

    # We register normally, then promote via direct DB call
    resp = client.post(f"{BASE_URL}/api/auth/register", json={
        "username": admin_name,
        "email": admin_email,
        "password": test_pass,
        "display_name": "Admin User"
    })
    assert_status(resp, 200, "Register admin user (will promote)")

    # Promote to admin using direct DB access
    from models.relational import SessionLocal as SetupDB, User as SetupUser
    setup_db = SetupDB()
    admin_user = setup_db.query(SetupUser).filter_by(username=admin_name).first()
    admin_user.role = "admin"
    setup_db.commit()
    setup_db.close()
    log("INFO", f"Promoted {admin_name} to admin role")

    # Login as admin
    form_data = {"grant_type": "password", "username": admin_name, "password": test_pass}
    resp = client.post(f"{BASE_URL}/api/auth/login", data=form_data)
    assert_status(resp, 200, "Login as admin")
    admin_token = resp.json()["access_token"]
    admin_client.headers["Authorization"] = f"Bearer {admin_token}"

    # Login as regular user (fresh token)
    form_data2 = {"grant_type": "password", "username": test_user, "password": test_pass}
    resp2 = client.post(f"{BASE_URL}/api/auth/login", data=form_data2)
    assert_status(resp2, 200, "Login as regular user")
    regular_token = resp2.json()["access_token"]
    auth_client.headers["Authorization"] = f"Bearer {regular_token}"

    return test_user, test_pass, regular_token, admin_token


# ═══════════════════════════════════════════════════════════════
# 1. HEALTH CHECKS
# ═══════════════════════════════════════════════════════════════
def test_health():
    section("1. HEALTH CHECKS")

    resp = client.get(f"{BASE_URL}/")
    assert_status(resp, 200, "Root health check")
    assert_eq(resp.json()["status"], "running", "Status is 'running'")

    resp = client.get(f"{BASE_URL}/api/health")
    assert_status(resp, 200, "Detailed health check")
    data = resp.json()
    assert_eq(data.get("postgres"), "healthy", "PostgreSQL healthy")
    assert_eq(data.get("mongodb"), "healthy", "MongoDB healthy")

    resp = client.get(f"{BASE_URL}/docs")
    assert_status(resp, 200, "Swagger docs accessible")

    resp = client.get(f"{BASE_URL}/openapi.json")
    assert_status(resp, 200, "OpenAPI schema accessible")


# ═══════════════════════════════════════════════════════════════
# 2. AUTHENTICATION
# ═══════════════════════════════════════════════════════════════
def test_auth():
    section("2. AUTHENTICATION")

    unique = str(uuid.uuid4())[:8]
    user = f"authtest_{unique}"

    # Register
    resp = client.post(f"{BASE_URL}/api/auth/register", json={
        "username": user,
        "email": f"{user}@test.com",
        "password": "secure123",
        "display_name": "Auth Tester"
    })
    assert_status(resp, 200, "Register new user")
    reg_data = resp.json()
    assert_contains(reg_data, "access_token", "Register returns token")
    assert_eq(reg_data["user"]["username"], user, "Correct username returned")
    assert_eq(reg_data["token_type"], "bearer", "Token type is bearer")

    # Me endpoint
    token = reg_data["access_token"]
    resp = client.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert_status(resp, 200, "GET /me returns user profile")
    me_data = resp.json()
    assert_eq(me_data["username"], user, "/me username matches")

    # Login
    form = {"grant_type": "password", "username": user, "password": "secure123"}
    resp = client.post(f"{BASE_URL}/api/auth/login", data=form)
    assert_status(resp, 200, "Login with correct password")
    login_data = resp.json()
    assert_contains(login_data, "access_token", "Login returns token")

    # Duplicate registration
    resp = client.post(f"{BASE_URL}/api/auth/register", json={
        "username": user,
        "email": f"{user}2@test.com",
        "password": "secure123",
    })
    assert_status(resp, 400, "Duplicate username rejected")

    # Invalid login
    form_bad = {"grant_type": "password", "username": user, "password": "wrongpass"}
    resp = client.post(f"{BASE_URL}/api/auth/login", data=form_bad)
    assert_status(resp, 401, "Wrong password rejected")

    # Missing auth
    resp = client.get(f"{BASE_URL}/api/auth/me")
    assert_status(resp, 401, "Unauthenticated /me rejected")

    # Invalid token
    resp = client.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert_status(resp, 401, "Invalid token rejected")


# ═══════════════════════════════════════════════════════════════
# 3. PRODUCTS API
# ═══════════════════════════════════════════════════════════════
def test_products():
    section("3. PRODUCTS API")

    # List products (no auth required)
    resp = client.get(f"{BASE_URL}/api/products/")
    assert_status(resp, 200, "List products")
    data = resp.json()
    assert_gt(data["total"], 0, "Product total > 0")
    assert_contains(data, "products", "Response has 'products'")
    assert_eq(data["page"], 1, "Default page is 1")
    assert_eq(len(data["products"]), 20, "Default limit is 20")
    assert_contains(data["products"][0], "product_id", "Product has product_id")
    assert_contains(data["products"][0], "category", "Product has category")
    assert_contains(data["products"][0], "unit_price", "Product has unit_price")
    assert_contains(data["products"][0], "stock_quantity", "Product has stock_quantity")

    # Pagination - page 2
    resp = client.get(f"{BASE_URL}/api/products/?page=2&limit=5")
    assert_status(resp, 200, "Pagination: page 2, limit 5")
    data = resp.json()
    assert_eq(data["page"], 2, "Page is 2")
    assert_eq(len(data["products"]), 5, "Returns 5 products")

    # Category filter
    resp = client.get(f"{BASE_URL}/api/products/?category=Electronics")
    assert_status(resp, 200, "Category filter: Electronics")
    data = resp.json()
    for p in data["products"]:
        assert_eq(p["category"], "Electronics", f"Product {p['product_id']} is Electronics")

    # Search
    resp = client.get(f"{BASE_URL}/api/products/?search=6")
    assert_status(resp, 200, "Search products by ID")
    data = resp.json()
    assert_gt(data["total"], 0, "Search returns results")

    # Get single product
    resp = client.get(f"{BASE_URL}/api/products/6")
    assert_status(resp, 200, "Get product by ID '6'")
    data = resp.json()
    assert_eq(data["product_id"], "6", "Correct product returned")

    # Product not found
    resp = client.get(f"{BASE_URL}/api/products/99999")
    assert_status(resp, 404, "Non-existent product returns 404")

    # Categories
    resp = client.get(f"{BASE_URL}/api/products/categories/all")
    assert_status(resp, 200, "List categories")
    data = resp.json()
    assert_contains(data, "categories", "Response has 'categories'")
    assert_gt(len(data["categories"]), 0, "At least one category")
    log("INFO", f"Categories: {', '.join(data['categories'])}")


# ═══════════════════════════════════════════════════════════════
# 4. CART / CLICKSTREAM API (MongoDB Bucket Pattern)
# ═══════════════════════════════════════════════════════════════
def test_cart_clickstream():
    section("4. CART & CLICKSTREAM (MongoDB)")

    session_id = f"test-session-{uuid.uuid4().hex[:8]}"

    # 4a. Record page_view
    resp = auth_client.post(f"{BASE_URL}/api/cart/event", json={
        "action_type": "page_view",
        "product_id": "6",
        "session_id": session_id,
    })
    assert_status(resp, 200, "Record page_view event")
    data = resp.json()
    assert_eq(data["status"], "recorded", "Event recorded")
    assert_eq(data["session_id"], session_id, "Session ID matches")
    assert_eq(data["action_type"], "page_view", "Action type correct")
    assert_eq(data["fraud_alert"], None, "No fraud for page_view")

    # 4b. Record add_to_cart
    resp = auth_client.post(f"{BASE_URL}/api/cart/event", json={
        "action_type": "add_to_cart",
        "product_id": "6",
        "session_id": session_id,
    })
    assert_status(resp, 200, "Record add_to_cart event")
    data = resp.json()
    assert_eq(data["action_type"], "add_to_cart", "Action type correct")

    # 4c. Record checkout
    resp = auth_client.post(f"{BASE_URL}/api/cart/event", json={
        "action_type": "checkout",
        "product_id": "6",
        "session_id": session_id,
    })
    assert_status(resp, 200, "Record checkout event")

    # 4d. Record purchase
    resp = auth_client.post(f"{BASE_URL}/api/cart/event", json={
        "action_type": "purchase",
        "product_id": "6",
        "session_id": session_id,
    })
    assert_status(resp, 200, "Record purchase event")

    # 4e. Invalid action_type
    resp = auth_client.post(f"{BASE_URL}/api/cart/event", json={
        "action_type": "invalid_type",
        "product_id": "6",
        "session_id": session_id,
    })
    assert_status(resp, 400, "Invalid action_type rejected")

    # 4f. Missing required fields
    resp = auth_client.post(f"{BASE_URL}/api/cart/event", json={
        "session_id": session_id,
    })
    assert_status(resp, 422, "Missing action_type returns 422")

    # 4g. Get session events
    resp = auth_client.get(f"{BASE_URL}/api/cart/session/{session_id}")
    assert_status(resp, 200, "Get session events")
    data = resp.json()
    assert_contains(data, "session_id", "Session response has session_id")
    assert_contains(data, "events", "Session response has events")
    assert_gt(len(data.get("events", [])), 0, "Session has recorded events")

    # 4h. Non-existent session
    resp = auth_client.get(f"{BASE_URL}/api/cart/session/nonexistent-session-12345")
    assert_status(resp, 404, "Non-existent session returns 404")

    # 4i. Auto-generated session_id
    resp = auth_client.post(f"{BASE_URL}/api/cart/event", json={
        "action_type": "page_view",
        "product_id": "6",
    })
    assert_status(resp, 200, "Event without session_id (auto-generated)")
    assert_contains(resp.json(), "session_id", "Session ID generated")


# ═══════════════════════════════════════════════════════════════
# 5. ORDERS API (PostgreSQL ACID + Triggers)
# ═══════════════════════════════════════════════════════════════
def test_orders():
    section("5. ORDERS (PostgreSQL ACID + Triggers)")

    # 5a. Create a valid order
    resp = auth_client.post(f"{BASE_URL}/api/orders/", json={
        "items": [
            {"product_id": "6", "quantity": 1},
            {"product_id": "770", "quantity": 2},
        ]
    })
    assert_status(resp, 200, "Create valid order")
    data = resp.json()
    assert_contains(data, "order_id", "Order has order_id")
    assert_contains(data, "items", "Order has items")
    assert_eq(data["status"], "confirmed", "Order status is confirmed")
    assert_gt(data["total_amount"], 0, "Total amount > 0")
    assert_eq(len(data["items"]), 2, "Two order items")
    order_id = data["order_id"]

    # 5b. Get order by ID
    resp = auth_client.get(f"{BASE_URL}/api/orders/{order_id}")
    assert_status(resp, 200, "Get order by ID")
    data = resp.json()
    assert_eq(data["order_id"], order_id, "Order ID matches")
    assert_eq(data["status"], "confirmed", "Status is confirmed")

    # 5c. List orders
    resp = auth_client.get(f"{BASE_URL}/api/orders/")
    assert_status(resp, 200, "List orders")
    data = resp.json()
    assert_contains(data, "orders", "Response has 'orders'")
    assert_gt(data["total"], 0, "At least one order")

    # 5d. Insufficient stock
    resp = auth_client.post(f"{BASE_URL}/api/orders/", json={
        "items": [
            {"product_id": "6", "quantity": 999999},
        ]
    })
    assert_status(resp, 400, "Insufficient stock rejected")

    # 5e. Invalid product
    resp = auth_client.post(f"{BASE_URL}/api/orders/", json={
        "items": [
            {"product_id": "NONEXISTENT", "quantity": 1},
        ]
    })
    assert_status(resp, 404, "Invalid product returns 404")

    # 5f. Empty items
    resp = auth_client.post(f"{BASE_URL}/api/orders/", json={"items": []})
    assert_status(resp, 400, "Empty items list rejected")

    # 5g. Order requires auth
    resp = client.post(f"{BASE_URL}/api/orders/", json={
        "items": [{"product_id": "6", "quantity": 1}]
    })
    assert_status(resp, 401, "Unauthenticated order rejected")

    # 5h. Verify trigger: Inventory Deduction
    resp_before = client.get(f"{BASE_URL}/api/products/6")
    stock_before = resp_before.json()["stock_quantity"]

    resp2 = auth_client.post(f"{BASE_URL}/api/orders/", json={
        "items": [{"product_id": "6", "quantity": 1}]
    })
    assert_status(resp2, 200, "Create order to test inventory deduction")

    resp_after = client.get(f"{BASE_URL}/api/products/6")
    stock_after = resp_after.json()["stock_quantity"]
    assert_eq(stock_after, stock_before - 1, "Inventory deducted by 1 (trigger)")

    # 5i. Verify trigger: Outbox (CDC)
    from models.relational import Outbox, SessionLocal as SL2
    db_out = SL2()
    outbox_count = db_out.query(Outbox).count()
    db_out.close()
    assert_gt(outbox_count, 0, "Outbox table has events (trigger)")


# ═══════════════════════════════════════════════════════════════
# 6. ANALYTICS API (Authenticated)
# ═══════════════════════════════════════════════════════════════
def test_analytics_authenticated():
    section("6. ANALYTICS (Authenticated)")

    # 6a. RFM Segmentation
    resp = auth_client.get(f"{BASE_URL}/api/analytics/rfm")
    assert_status(resp, 200, "RFM segmentation")
    data = resp.json()
    assert_contains(data, "segments", "RFM has 'segments'")
    assert_gt(len(data["segments"]), 0, "RFM returns results")
    # Check for known segments
    segments_found = set(s.get("segment") for s in data["segments"] if s.get("segment"))
    valid = {"Champions", "Loyal Customers", "Potential Loyalists", "At Risk", "Lost"}
    overlap = segments_found & valid
    assert_gt(len(overlap), 0, f"Known RFM segments found: {overlap}")

    # 6b. Market Basket Analysis
    resp = auth_client.get(f"{BASE_URL}/api/analytics/market-basket?top_n=5")
    assert_status(resp, 200, "Market basket analysis")
    data = resp.json()
    assert_contains(data, "pairs", "Market basket has 'pairs'")
    if data["pairs"]:
        assert_contains(data["pairs"][0], "product_a", "Pair has product_a")
        assert_contains(data["pairs"][0], "product_b", "Pair has product_b")
        assert_contains(data["pairs"][0], "pair_count", "Pair has pair_count")

    # 6c. Funnel Analysis
    resp = auth_client.get(f"{BASE_URL}/api/analytics/funnel")
    assert_status(resp, 200, "Funnel analysis")
    data = resp.json()
    assert_contains(data, "funnel", "Funnel has 'funnel'")
    stages = [f["stage"] for f in data["funnel"]]
    for s in ["page_view", "add_to_cart", "checkout", "purchase"]:
        assert_eq(s in stages, True, f"Funnel includes '{s}'")
    # Conversion rates should descend
    if len(data["funnel"]) >= 2:
        rates = [f["conversion_rate"] for f in data["funnel"]]
        assert_eq(all(rates[i] >= rates[i+1] for i in range(len(rates)-1)), True,
                  "Conversion rates are non-increasing")

    # 6d. Cart Abandonment
    resp = auth_client.get(f"{BASE_URL}/api/analytics/cart-abandonment")
    assert_status(resp, 200, "Cart abandonment")
    data = resp.json()
    assert_contains(data, "abandoned_sessions", "Response has 'abandoned_sessions'")

    # 6e. Top Products
    resp = auth_client.get(f"{BASE_URL}/api/analytics/top-products?limit=5")
    assert_status(resp, 200, "Top products")
    data = resp.json()
    assert_contains(data, "products", "Response has 'products'")
    assert_gt(len(data["products"]), 0, "Top products returns results")
    assert_contains(data["products"][0], "total_sold", "Product has total_sold")
    assert_contains(data["products"][0], "total_revenue", "Product has total_revenue")

    # 6f. Sales by Category
    resp = auth_client.get(f"{BASE_URL}/api/analytics/sales-by-category")
    assert_status(resp, 200, "Sales by category")
    data = resp.json()
    assert_contains(data, "categories", "Response has 'categories'")
    assert_gt(len(data["categories"]), 0, "Sales by category returns results")


# ═══════════════════════════════════════════════════════════════
# 7. ANALYTICS API (Admin Only)
# ═══════════════════════════════════════════════════════════════
def test_analytics_admin():
    section("7. ANALYTICS (Admin Only)")

    # 7a. Alerts — admin can access
    resp = admin_client.get(f"{BASE_URL}/api/analytics/alerts")
    assert_status(resp, 200, "Admin can access alerts")
    data = resp.json()
    assert_contains(data, "alerts", "Alerts response has 'alerts'")
    assert_contains(data, "count", "Alerts response has 'count'")

    # 7b. Alerts — non-admin cannot access
    resp = auth_client.get(f"{BASE_URL}/api/analytics/alerts")
    assert_status(resp, 403, "Non-admin blocked from alerts")

    # 7c. Audit trail — admin can access
    # First create an order to have something to audit
    resp = auth_client.post(f"{BASE_URL}/api/orders/", json={
        "items": [{"product_id": "770", "quantity": 1}]
    })
    if resp.status_code == 200:
        order_id = resp.json()["order_id"]
        resp = admin_client.get(f"{BASE_URL}/api/analytics/audit/{order_id}")
        assert_status(resp, 200, "Admin can access audit trail")
        data = resp.json()
        assert_eq(data["order_id"], order_id, "Audit order ID matches")

    # 7d. Audit trail — non-admin blocked
    resp = auth_client.get(f"{BASE_URL}/api/analytics/audit/some-order-id")
    assert_status(resp, 403, "Non-admin blocked from audit")

    # 7e. Audit trail — requires auth
    resp = client.get(f"{BASE_URL}/api/analytics/audit/some-order-id")
    assert_status(resp, 401, "Unauthenticated audit rejected")


# ═══════════════════════════════════════════════════════════════
# 8. TRIGGER VERIFICATION (PostgreSQL)
# ═══════════════════════════════════════════════════════════════
def test_triggers():
    section("8. TRIGGER VERIFICATION")

    from sqlalchemy import text
    from models.relational import SessionLocal

    db = SessionLocal()

    # 8a. Stock Check Trigger (BEFORE INSERT on order_items)
    r = db.execute(text(
        "SELECT proname FROM pg_proc WHERE proname='check_stock_before_order'"
    )).fetchone()
    assert_eq(r is not None, True, "Stock check trigger function exists")

    # 8b. Inventory Deduction Trigger (AFTER INSERT on order_items)
    r = db.execute(text(
        "SELECT proname FROM pg_proc WHERE proname='deduct_inventory_after_order'"
    )).fetchone()
    assert_eq(r is not None, True, "Inventory deduction trigger function exists")

    # 8c. Outbox Trigger (AFTER INSERT on orders)
    r = db.execute(text(
        "SELECT proname FROM pg_proc WHERE proname='outbox_on_order_created'"
    )).fetchone()
    assert_eq(r is not None, True, "Outbox trigger function exists")

    # 8d. Audit Trigger (AFTER UPDATE on orders)
    r = db.execute(text(
        "SELECT proname FROM pg_proc WHERE proname='audit_order_status_change'"
    )).fetchone()
    assert_eq(r is not None, True, "Audit trigger function exists")

    # 8e. Stock constraint CHECK (stock_quantity >= 0)
    # SQLAlchemy generates constraint name; check any constraint on stock_quantity
    r = db.execute(text(
        "SELECT conname FROM pg_constraint "
        "JOIN pg_attribute ON pg_attribute.attrelid = conrelid AND pg_attribute.attnum = ANY(conkey) "
        "WHERE conrelid='products'::regclass AND pg_attribute.attname='stock_quantity'"
    )).fetchone()
    assert_eq(r is not None, True, "Stock non-negative CHECK constraint exists")

    db.close()

    # 8f. Verify outbox is being populated (functional test)
    from models.relational import Outbox
    db2 = SessionLocal()
    count = db2.query(Outbox).count()
    db2.close()
    assert_gt(count, 0, "Outbox table populated by trigger")

    # 8g. Verify trigger names attached to tables
    db3 = SessionLocal()
    triggers = db3.execute(text(
        "SELECT tgname FROM pg_trigger WHERE tgname LIKE 'trg_%' ORDER BY tgname"
    )).fetchall()
    trigger_names = [t[0] for t in triggers]
    for expected in ["trg_check_stock", "trg_deduct_inventory", "trg_outbox_order", "trg_audit_order"]:
        assert_eq(expected in trigger_names, True, f"Trigger '{expected}' attached to table")
    db3.close()


# ═══════════════════════════════════════════════════════════════
# 9. MONGODB VERIFICATION
# ═══════════════════════════════════════════════════════════════
def test_mongodb():
    section("9. MONGODB VERIFICATION")

    import asyncio
    from services.nosql_service import get_mongo_db

    async def check_mongo():
        db = await get_mongo_db()

        # 9a. Collections
        cols = await db.list_collection_names()
        required = ["user_sessions", "session_stats", "customer_order_summary", "funnel_metrics"]
        for col in required:
            assert_eq(col in cols, True, f"MongoDB collection '{col}' exists")
        log("INFO", f"Collections: {sorted(cols)}")

        # 9b. Indexes on user_sessions
        indexes = await db.user_sessions.index_information()
        idx_names = list(indexes.keys())
        log("INFO", f"Indexes on user_sessions: {idx_names}")
        assert_eq("customer_id_1_session_id_1" in idx_names, True,
                  "Compound index on (customer_id, session_id)")
        assert_eq("end_time_1" in idx_names, True,
                  "TTL index on end_time")
        assert_eq("flagged_1" in idx_names, True,
                  "Index on flagged field")
        assert_eq("events.timestamp_1" in idx_names, True,
                  "Index on events.timestamp")

        # 9c. Verify data in user_sessions (functional)
        count = await db.user_sessions.count_documents({})
        assert_gt(count, 0, "user_sessions has documents")

    asyncio.run(check_mongo())


# ═══════════════════════════════════════════════════════════════
# 10. ERROR HANDLING & EDGE CASES
# ═══════════════════════════════════════════════════════════════
def test_error_handling():
    section("10. ERROR HANDLING & EDGE CASES")

    # 10a. Missing JSON body
    resp = client.post(f"{BASE_URL}/api/auth/register", content=b"", headers={"Content-Type": "application/json"})
    assert_status(resp, 422, "Empty POST body returns 422")

    # 10b. Short username
    resp = client.post(f"{BASE_URL}/api/auth/register", json={
        "username": "ab", "email": "short@test.com", "password": "123456"
    })
    assert_status(resp, 400, "Short username rejected")

    # 10c. Invalid email
    resp = client.post(f"{BASE_URL}/api/auth/register", json={
        "username": "validuser123", "email": "notanemail", "password": "123456"
    })
    assert_status(resp, 400, "Invalid email rejected")

    # 10d. Short password
    resp = client.post(f"{BASE_URL}/api/auth/register", json={
        "username": "validuser456", "email": "valid@test.com", "password": "123"
    })
    assert_status(resp, 400, "Short password rejected")

    # 10e. Non-existent route
    resp = client.get(f"{BASE_URL}/api/nonexistent")
    assert_status(resp, 404, "Non-existent route returns 404")

    # 10f. Invalid pagination params
    resp = client.get(f"{BASE_URL}/api/products/?page=0&limit=200")
    assert_status(resp, 422, "Invalid page/limit returns 422")


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    global PASS, FAIL, ERRORS

    print("\n" + "█"*60)
    print("█  INF2003 Group 11 — Comprehensive Test Suite")
    print("█  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("█"*60)

    start_time = time.time()

    # Setup
    test_user, test_pass, regular_token, admin_token = setup()

    # Run all test groups
    try:
        test_health()
    except Exception as e:
        FAIL += 1
        ERRORS.append(f"Health checks crashed: {e}")
        log("FAIL", f"Health checks crashed: {e}")

    try:
        test_auth()
    except Exception as e:
        FAIL += 1
        ERRORS.append(f"Auth tests crashed: {e}")
        log("FAIL", f"Auth tests crashed: {e}")

    try:
        test_products()
    except Exception as e:
        FAIL += 1
        ERRORS.append(f"Product tests crashed: {e}")
        log("FAIL", f"Product tests crashed: {e}")

    try:
        test_cart_clickstream()
    except Exception as e:
        FAIL += 1
        ERRORS.append(f"Cart tests crashed: {e}")
        log("FAIL", f"Cart tests crashed: {e}")

    try:
        test_orders()
    except Exception as e:
        FAIL += 1
        ERRORS.append(f"Order tests crashed: {e}")
        log("FAIL", f"Order tests crashed: {e}")

    try:
        test_analytics_authenticated()
    except Exception as e:
        FAIL += 1
        ERRORS.append(f"Analytics tests crashed: {e}")
        log("FAIL", f"Analytics tests crashed: {e}")

    try:
        test_analytics_admin()
    except Exception as e:
        FAIL += 1
        ERRORS.append(f"Admin analytics tests crashed: {e}")
        log("FAIL", f"Admin analytics tests crashed: {e}")

    try:
        test_triggers()
    except Exception as e:
        FAIL += 1
        ERRORS.append(f"Trigger tests crashed: {e}")
        log("FAIL", f"Trigger tests crashed: {e}")

    try:
        test_mongodb()
    except Exception as e:
        FAIL += 1
        ERRORS.append(f"MongoDB tests crashed: {e}")
        log("FAIL", f"MongoDB tests crashed: {e}")

    try:
        test_error_handling()
    except Exception as e:
        FAIL += 1
        ERRORS.append(f"Error handling tests crashed: {e}")
        log("FAIL", f"Error handling tests crashed: {e}")

    elapsed = time.time() - start_time

    # ── Summary ──────────────────────────────────────────
    total = PASS + FAIL
    print(f"\n{'═'*60}")
    print("  RESULTS")
    print(f"{'═'*60}")
    print(f"  ✅ Passed:  {PASS}/{total}")
    print(f"  ❌ Failed:  {FAIL}/{total}")
    print(f"  ⏱️  Time:    {elapsed:.2f}s")
    print(f"{'═'*60}")

    if ERRORS:
        print(f"\n  🔴 FAILURES ({len(ERRORS)}):")
        for err in ERRORS:
            print(f"     • {err}")

    if FAIL == 0:
        print("\n  🎉 ALL TESTS PASSED!")
    else:
        print(f"\n  ⚠️  {FAIL} test(s) failed. See details above.")

    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
