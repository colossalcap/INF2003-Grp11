# Entity-Relationship Diagram & Database Design

**INF2003 Group 11 — E-Commerce Clickstream & Transaction Analytics**

---

## 1. PostgreSQL — Relational Database (ACID)

### 1.1 Complete Entity-Relationship Diagram

```
┌──────────────────────────┐       ┌──────────────────────────┐
│         users            │       │        customers         │
├──────────────────────────┤       ├──────────────────────────┤
│ PK  user_id       INT    │       │ PK  customer_id   UUID   │
│     username      VARCHAR│       │     registration_date    │
│     email         VARCHAR│       │       TIMESTAMP          │
│     password_hash VARCHAR│       │     country_code  CHAR(3)│
│     display_name  VARCHAR│       │     opt_in_status BOOLEAN│
│     role          VARCHAR│       └───────────┬──────────────┘
│     created_at    TIMESTMP│                  │ 1:M
└──────────────────────────┘                   │
                                               ▼
┌──────────────────────────┐       ┌──────────────────────────┐
│         orders           │       │        products          │
├──────────────────────────┤       ├──────────────────────────┤
│ PK  order_id      UUID   │       │ PK  product_id    VARCHAR│
│ FK  customer_id   UUID   │───┐   │     category      VARCHAR│
│     order_date    TIMESTMP│  │   │     unit_price    DECIMAL │
│     total_amount  DECIMAL │  │   │     stock_quantity INTEGER│
│     status        VARCHAR │  │   │ CHECK (stock >= 0)       │
└──────────┬────────────────┘  │   └────────────┬─────────────┘
           │ 1:M               │                │ M:1
           ▼                   │                ▼
┌──────────────────────────┐   │   ┌──────────────────────────┐
│       order_items        │   │   │         outbox           │
├──────────────────────────┤   │   │   (CDC / Event Store)    │
│ PK  item_id       SERIAL │   │   ├──────────────────────────┤
│ FK  order_id      UUID   │◄──┘   │ PK  event_id      SERIAL │
│ FK  product_id    VARCHAR│───────│     aggregate_id  VARCHAR│
│     quantity      INTEGER│       │     event_type    VARCHAR│
│ CHECK (quantity > 0)     │       │     payload       JSONB  │
└──────────────────────────┘       │     created_at    TIMESTMP│
                                   │     processed     BOOLEAN│
┌──────────────────────────┐       └──────────────────────────┘
│     order_audit_log      │
│   (Trigger-populated)    │       ┌──────────────────────────┐
├──────────────────────────┤       │         alerts           │
│ PK  audit_id      SERIAL │       │   (Fraud Detection)      │
│ FK  order_id       UUID  │       ├──────────────────────────┤
│     changed_by    VARCHAR│       │ PK  alert_id      SERIAL │
│     field_name    VARCHAR│       │     customer_id   UUID   │
│     old_value      TEXT  │       │     message        TEXT  │
│     new_value      TEXT  │       │     alert_type    VARCHAR│
│     changed_at    TIMESTMP│      │     created_at    TIMESTMP│
└──────────────────────────┘       │     acknowledged  BOOLEAN│
                                   └──────────────────────────┘
```

### 1.2 Table Details

#### `users` — Authentication Accounts
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | INT | PK, AUTO-INCREMENT | Unique user identifier |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL, INDEXED | Login username |
| `email` | VARCHAR(100) | UNIQUE, NOT NULL | Email address |
| `password_hash` | VARCHAR(255) | NOT NULL | bcrypt-hashed password |
| `display_name` | VARCHAR(100) | — | Display name for UI |
| `role` | VARCHAR(20) | DEFAULT 'customer' | 'customer' or 'admin' |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Account creation time |

> **~20,000 rows** (one per customer from data loader + manually registered users)

#### `customers` — Customer Profiles
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `customer_id` | UUID | PK | Globally unique customer ID |
| `registration_date` | TIMESTAMP | DEFAULT NOW() | When customer was created |
| `country_code` | VARCHAR(3) | — | ISO country code |
| `opt_in_status` | BOOLEAN | DEFAULT TRUE | Marketing opt-in flag |

> **~20,000 rows** — PK is UUID (not auto-increment) to prevent enumeration attacks

#### `products` — Product Catalog
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `product_id` | VARCHAR(50) | PK | Product identifier |
| `category` | VARCHAR(100) | NOT NULL, INDEXED | Product category (7 values) |
| `unit_price` | DOUBLE PRECISION | NOT NULL | Price per unit in USD |
| `stock_quantity` | INTEGER | NOT NULL, CHECK(>= 0) | Current stock level |

> **1,197 rows** — 7 categories: Beauty, Books, Electronics, Fashion, Home & Kitchen, Sports, Toys

#### `orders` — Purchase Orders
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `order_id` | UUID | PK | Unique order identifier |
| `customer_id` | UUID | FK → customers, NOT NULL | Customer who placed the order |
| `order_date` | TIMESTAMP | DEFAULT NOW() | When the order was placed |
| `total_amount` | DOUBLE PRECISION | DEFAULT 0.0 | Sum of all line item totals |
| `status` | VARCHAR(20) | DEFAULT 'pending' | Order status |

> **~53,000 rows** — One-to-many from customers

#### `order_items` — Line Items
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `item_id` | SERIAL | PK | Auto-incrementing line item ID |
| `order_id` | UUID | FK → orders, NOT NULL, ON DELETE CASCADE | Parent order |
| `product_id` | VARCHAR(50) | FK → products, NOT NULL | Product ordered |
| `quantity` | INTEGER | NOT NULL, CHECK(> 0) | Quantity ordered |

> **~75,000 rows** — Triggers fire on this table: stock check (BEFORE INSERT), inventory deduction (AFTER INSERT)

#### `outbox` — CDC Event Store
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `event_id` | SERIAL | PK | Auto-incrementing event ID |
| `aggregate_id` | VARCHAR(255) | NOT NULL | ID of the entity (order_id) |
| `event_type` | VARCHAR(100) | NOT NULL | Event type (e.g., 'order_created') |
| `payload` | JSONB | NOT NULL | Event data as JSON |
| `created_at` | TIMESTAMP | DEFAULT NOW() | When the event was created |
| `processed` | BOOLEAN | DEFAULT FALSE | Has the CDC processor handled this? |

> **Dynamic** — grows with each new order. CDC processor marks `processed = TRUE` after syncing.

#### `order_audit_log` — Change History
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `audit_id` | SERIAL | PK | Auto-incrementing audit entry |
| `order_id` | UUID | NOT NULL, INDEXED | Which order changed |
| `changed_by` | VARCHAR(50) | — | Who made the change |
| `field_name` | VARCHAR(100) | — | Which field changed |
| `old_value` | TEXT | — | Previous value |
| `new_value` | TEXT | — | New value |
| `changed_at` | TIMESTAMP | DEFAULT NOW() | When the change happened |

> **Dynamic** — populated by `trg_audit_order` trigger on order status/total updates

#### `alerts` — Fraud Detection Results
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `alert_id` | SERIAL | PK | Auto-incrementing alert ID |
| `customer_id` | UUID | — | Customer who triggered the alert |
| `message` | TEXT | — | Alert description |
| `alert_type` | VARCHAR(50) | — | Type of alert (e.g., 'fraud') |
| `created_at` | TIMESTAMP | DEFAULT NOW() | When alert was generated |
| `acknowledged` | BOOLEAN | DEFAULT FALSE | Has the alert been reviewed? |

---

### 1.3 Relationship Types

| Relationship | Type | Parent → Child | Implementation |
|-------------|------|----------------|----------------|
| Customer → Order | **1 : M** | customers → orders | FK `customer_id` in `orders` REFERENCES `customers(customer_id)` |
| Order → OrderItem | **1 : M** | orders → order_items | FK `order_id` in `order_items` REFERENCES `orders(order_id)` ON DELETE CASCADE |
| Product → OrderItem | **1 : M** | products → order_items | FK `product_id` in `order_items` REFERENCES `products(product_id)` |

> **Note:** The `users` table is independent — there is no FK relationship between `users` and `customers`. This allows anonymous browsing data in MongoDB while authentication is handled separately.

---

### 1.4 PostgreSQL Triggers (4)

| # | Trigger Name | Fires On | Timing | Function | Purpose |
|---|-------------|----------|--------|----------|---------|
| 1 | `trg_check_stock` | `order_items` | BEFORE INSERT | `check_stock_before_order()` | Raises exception if `stock_quantity < requested quantity` |
| 2 | `trg_deduct_inventory` | `order_items` | AFTER INSERT | `deduct_inventory_after_order()` | Decrements `products.stock_quantity` by `order_items.quantity` |
| 3 | `trg_outbox_order` | `orders` | AFTER INSERT | `outbox_on_order_created()` | Writes JSON event to `outbox` table for CDC sync to MongoDB |
| 4 | `trg_audit_order` | `orders` | AFTER UPDATE | `audit_order_status_change()` | Logs old → new values when `status` or `total_amount` changes |

**Trigger execution flow during order creation:**
```
1. INSERT INTO orders          → trg_outbox_order fires → outbox row created
2. INSERT INTO order_items     → trg_check_stock fires → validates stock
                               → trg_deduct_inventory fires → stock decremented
3. COMMIT                      → all succeed or all roll back
4. UPDATE orders SET status    → trg_audit_order fires → change logged
```

---

## 2. MongoDB — NoSQL Document Store (BASE)

### 2.1 Collections Overview

| # | Collection | Design Pattern | Document Count | Indexes |
|---|-----------|---------------|---------------|---------|
| 1 | `user_sessions` | **Bucket** | ~27,500 | Compound (customer_id, session_id) UNIQUE, TTL (end_time, 30-day), flagged, events.timestamp |
| 2 | `session_stats` | **Computed** | ~27,500 | session_id UNIQUE |
| 3 | `customer_order_summary` | **CDC Target** | ~20,000 | customer_id UNIQUE |
| 4 | `funnel_metrics` | **Cached** | on-demand | (stage, computed_at) |

### 2.2 Document Schemas

#### `user_sessions` — Bucket Pattern
```json
{
  "_id": "ObjectId('...')",
  "customer_id": "20006",
  "session_id": "07e595ab-1234-5678-9abc-def012345678",
  "start_time": "2026-06-29T07:51:00.000Z",
  "end_time": "2026-06-29T07:52:30.000Z",
  "event_count": 15,
  "flagged": false,
  "events": [
    {
      "action_type": "page_view",
      "product_id": "6",
      "timestamp": "2026-06-29T07:51:05.000Z"
    },
    {
      "action_type": "add_to_cart",
      "product_id": "6",
      "timestamp": "2026-06-29T07:51:10.000Z"
    }
  ]
}
```

**Operations:**
- **Insert event:** `updateOne` with `$push` (events) + `$inc` (event_count) + `$set` (end_time) + `$setOnInsert` (start_time, flagged) — upsert creates document on first event
- **Fraud check:** Query events in time window, count `add_to_cart` without `purchase`, set `flagged: true` if threshold exceeded
- **TTL index:** `end_time` with `expireAfterSeconds: 2592000` (30 days) — auto-deletes stale sessions

#### `session_stats` — Computed Pattern
```json
{
  "_id": "ObjectId('...')",
  "session_id": "07e595ab-...",
  "customer_id": "20006",
  "start_time": "2026-06-29T07:51:00.000Z",
  "end_time": "2026-06-29T07:52:30.000Z",
  "total_events": 15,
  "page_views": 2,
  "add_to_carts": 11,
  "checkouts": 1,
  "purchases": 1,
  "duration_seconds": 90
}
```

#### `customer_order_summary` — CDC Target
```json
{
  "_id": "ObjectId('...')",
  "customer_id": "20006",
  "total_orders": 5,
  "total_spent": 1247.83,
  "last_order_date": "2026-06-29T07:51:00.000Z",
  "last_updated": "2026-06-29T07:51:05.000Z"
}
```

**How it's populated:** PostgreSQL `trg_outbox_order` writes to `outbox` → `sync_service.py` polls `outbox WHERE processed = false` → `update_customer_order_summary()` uses `$inc` (total_orders, total_spent) + `$set` (last_order_date) + upsert.

#### `funnel_metrics` — Cached Pattern
```json
{
  "_id": "ObjectId('...')",
  "stage": "page_view",
  "count": 120000,
  "conversion_rate": 100.0,
  "computed_at": "2026-06-29T08:00:00.000Z"
}
```

**Computed via:** MongoDB aggregation pipeline with `$facet` — runs 4 parallel counts and calculates conversion rates.

---

### 2.3 Indexes

| Collection | Index | Type | Purpose |
|-----------|-------|------|---------|
| `user_sessions` | `{customer_id: 1, session_id: 1}` | Compound UNIQUE | Fast session lookup, prevents duplicate sessions |
| `user_sessions` | `{end_time: 1}` | TTL (30 days) | Auto-delete sessions older than 30 days |
| `user_sessions` | `{flagged: 1}` | Single field | Quick fraud flag queries |
| `user_sessions` | `{events.timestamp: 1}` | Nested field | Time-range queries on events |
| `session_stats` | `{session_id: 1}` | UNIQUE | One stat document per session |
| `customer_order_summary` | `{customer_id: 1}` | UNIQUE | One summary document per customer |
| `funnel_metrics` | `{stage: 1, computed_at: -1}` | Compound | Latest funnel computation per stage |

---

### 2.4 Design Pattern Justification

| Pattern | Why This Project Uses It |
|---------|--------------------------|
| **Bucket Pattern** | Groups 100+ clickstream events per session into one document. Avoids the "one document per event" anti-pattern that causes exponential index growth. `$push` + `$inc` are O(1) operations. |
| **Computed Pattern** | Pre-aggregates session stats so the dashboard doesn't re-compute on every load. Trade-off: slight staleness for massive read speed improvement. |
| **CDC Target** | `customer_order_summary` is a denormalized view of PostgreSQL orders. Avoids expensive cross-database JOINs — all customer order data needed for dashboards is in one document. |
| **Cached Pattern** | `funnel_metrics` results are computed once and cached. The `$facet` aggregation scans all sessions, which is expensive — running it on-demand and caching avoids repeated computation. |

---

## 3. Cross-Database Data Flow (CDC)

```
┌─────────────────────┐         ┌──────────────────────────┐
│    PostgreSQL        │         │       MongoDB             │
│                      │         │                           │
│  orders INSERT       │         │                           │
│      │               │         │                           │
│      ▼               │         │                           │
│  trg_outbox_order    │         │                           │
│      │               │         │                           │
│      ▼               │         │                           │
│  outbox table ────────────────► sync_service.py            │
│  {                   │  poll   │   │                       │
│    event_type:       │  every  │   ▼                       │
│    "order_created",  │  5 sec  │  update_customer_order_   │
│    payload: {...},   │─────────│  summary()                │
│    processed: false  │         │   │                       │
│  }                   │         │   ▼                       │
│                      │         │  customer_order_summary   │
│                      │         │  {                        │
│                      │         │    total_orders: $inc 1   │
│                      │         │    total_spent: $inc amt  │
│                      │         │  }                        │
└─────────────────────┘         └──────────────────────────┘
```

**Consistency model:** PostgreSQL is the source of truth (ACID). MongoDB is eventually consistent (~5 second lag). If the poller crashes, unprocessed events are retried on restart.

---

## 4. Data Volumes

| Database | Object | Approximate Count |
|----------|--------|-------------------|
| PostgreSQL | `users` | ~20,000 |
| PostgreSQL | `customers` | ~20,000 |
| PostgreSQL | `products` | 1,197 |
| PostgreSQL | `orders` | ~53,000 |
| PostgreSQL | `order_items` | ~75,000 |
| PostgreSQL | `outbox` | ~53,000 (grows with orders) |
| PostgreSQL | `order_audit_log` | Dynamic |
| PostgreSQL | `alerts` | Dynamic |
| MongoDB | `user_sessions` | ~27,500 |
| MongoDB | `session_stats` | ~27,500 |
| MongoDB | `customer_order_summary` | ~20,000 |
| MongoDB | `funnel_metrics` | 4 (one per stage) |

**Total: 8 relational tables + 4 MongoDB collections — ~275,000 rows across both databases**

---

*INF2003 Group 11 — Team Hanzalians — June 2026*
