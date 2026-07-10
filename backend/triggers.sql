-- ============================================================
-- INF2003 Group 11 — PostgreSQL Trigger Definitions
-- Automatically executed on container startup via
-- /docker-entrypoint-initdb.d/01_triggers.sql
-- Also creates the core tables the triggers depend on.
-- ============================================================

-- ============================================================
-- 0. CORE TABLES (created here so triggers can reference them)
--    The ORM will see these exist and skip recreation.
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    user_id         SERIAL PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    email           VARCHAR(100) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    display_name    VARCHAR(100),
    role            VARCHAR(20) DEFAULT 'customer',
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id     UUID PRIMARY KEY,
    user_id         INTEGER REFERENCES users(user_id),
    registration_date TIMESTAMP DEFAULT NOW(),
    country_code    VARCHAR(3),
    opt_in_status   BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS products (
    product_id      VARCHAR(50) PRIMARY KEY,
    name            VARCHAR(255) NOT NULL DEFAULT 'Unknown Product',
    category        VARCHAR(100) NOT NULL,
    unit_price      DOUBLE PRECISION NOT NULL,
    stock_quantity  INTEGER NOT NULL CHECK (stock_quantity >= 0)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id        UUID PRIMARY KEY,
    customer_id     UUID NOT NULL REFERENCES customers(customer_id),
    order_date      TIMESTAMP DEFAULT NOW(),
    total_amount    DOUBLE PRECISION DEFAULT 0.0,
    status          VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS order_items (
    item_id         SERIAL PRIMARY KEY,
    order_id        UUID NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id      VARCHAR(50) NOT NULL REFERENCES products(product_id),
    quantity        INTEGER NOT NULL CHECK (quantity > 0)
);

CREATE TABLE IF NOT EXISTS outbox (
    event_id        SERIAL PRIMARY KEY,
    aggregate_id    VARCHAR(255) NOT NULL,
    event_type      VARCHAR(100) NOT NULL,
    payload         JSONB NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW(),
    processed       BOOLEAN DEFAULT FALSE
);

-- ============================================================
-- 1. ORDER AUDIT LOG TABLE (required for Audit Trigger)
-- ============================================================
CREATE TABLE IF NOT EXISTS order_audit_log (
    audit_id        SERIAL PRIMARY KEY,
    order_id        UUID NOT NULL,
    changed_by      VARCHAR(50),
    field_name      VARCHAR(100),
    old_value       TEXT,
    new_value       TEXT,
    changed_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_order_id ON order_audit_log(order_id);

-- ============================================================
-- 2. STOCK CHECK TRIGGER (BEFORE INSERT on order_items)
--    Raises exception if insufficient stock.
-- ============================================================
CREATE OR REPLACE FUNCTION check_stock_before_order()
RETURNS TRIGGER AS $$
DECLARE
    available_stock INTEGER;
BEGIN
    SELECT stock_quantity INTO available_stock
    FROM products
    WHERE product_id = NEW.product_id;

    IF available_stock IS NULL THEN
        RAISE EXCEPTION 'Product % does not exist.', NEW.product_id;
    END IF;

    IF available_stock < NEW.quantity THEN
        RAISE EXCEPTION 'Insufficient stock for product %. Available: %, Requested: %.',
            NEW.product_id, available_stock, NEW.quantity;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_check_stock ON order_items;
CREATE TRIGGER trg_check_stock
    BEFORE INSERT ON order_items
    FOR EACH ROW
    EXECUTE FUNCTION check_stock_before_order();

-- ============================================================
-- 3. INVENTORY DEDUCTION TRIGGER (AFTER INSERT on order_items)
--    Decrements stock_quantity after a successful order item insert.
-- ============================================================
CREATE OR REPLACE FUNCTION deduct_inventory_after_order()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE products
    SET stock_quantity = stock_quantity - NEW.quantity
    WHERE product_id = NEW.product_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_deduct_inventory ON order_items;
CREATE TRIGGER trg_deduct_inventory
    AFTER INSERT ON order_items
    FOR EACH ROW
    EXECUTE FUNCTION deduct_inventory_after_order();

-- ============================================================
-- 4. OUTBOX TRIGGER (AFTER INSERT on orders)
--    Inserts a JSON event into the outbox table for CDC.
-- ============================================================
CREATE OR REPLACE FUNCTION outbox_on_order_created()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO outbox (aggregate_id, event_type, payload)
    VALUES (
        NEW.order_id::TEXT,
        'order_created',
        jsonb_build_object(
            'order_id', NEW.order_id,
            'customer_id', NEW.customer_id,
            'total_amount', NEW.total_amount,
            'order_date', NEW.order_date,
            'status', NEW.status
        )
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_outbox_order ON orders;
CREATE TRIGGER trg_outbox_order
    AFTER INSERT ON orders
    FOR EACH ROW
    EXECUTE FUNCTION outbox_on_order_created();

-- ============================================================
-- 5. AUDIT TRIGGER (AFTER UPDATE on orders)
--    Logs old/new values when order status changes.
-- ============================================================
CREATE OR REPLACE FUNCTION audit_order_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO order_audit_log (order_id, changed_by, field_name, old_value, new_value)
        VALUES (NEW.order_id, 'system', 'status', OLD.status, NEW.status);

        -- Also log total_amount changes
        IF OLD.total_amount IS DISTINCT FROM NEW.total_amount THEN
            INSERT INTO order_audit_log (order_id, changed_by, field_name, old_value, new_value)
            VALUES (NEW.order_id, 'system', 'total_amount',
                    OLD.total_amount::TEXT, NEW.total_amount::TEXT);
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_audit_order ON orders;
CREATE TRIGGER trg_audit_order
    AFTER UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION audit_order_status_change();
