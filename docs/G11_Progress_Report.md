# G11 — Progress Report
## INF2003 Group Project — E-Commerce Clickstream & Transaction Analytics

> **Submission:** `G11_Progress Report.pdf` &middot; Max 4 pages (excluding cover)

---

## Cover Page

| Field | Detail |
|-------|--------|
| **Module** | INF2003 Database Design & Implementation |
| **Group ID** | G11 |
| **Project Title** | E-Commerce Clickstream & Transaction Analytics |
| **Topic** | Topic 2 — Dual-Database Analytics Platform |
| **Team Members** | Tan Ding Mao (Team Lead), [Member 2], [Member 3], [Member 4] |
| **Team Lead Contact** | [your-email@example.com] |
| **Submission Date** | June 22, 2026 |

---

## 1. Application Background & Problem Statement

### 1.1 Background

E-commerce platforms process tens of thousands of transactions daily alongside millions of clickstream events. These two data categories have fundamentally opposing requirements: orders and inventory demand strict **ACID** guarantees (Atomicity, Consistency, Isolation, Durability) — a partial inventory deduction or double-charge is unacceptable. Meanwhile, user behaviour data such as page views, cart additions, and session flows is write-heavy, schema-flexible, and best served by **BASE** (Basically Available, Soft-state, Eventually consistent) systems that prioritise throughput over immediate consistency.

Traditional monolithic architectures force one database paradigm to serve both workloads, resulting in either fragile relational schemas that require constant migration for evolving clickstream metadata, or NoSQL systems that lack the transactional integrity needed for payment processing. A **polyglot persistence** approach — using the right database for each data shape — addresses this impedance mismatch directly.

### 1.2 Problem Statement

Online retailers face three interconnected challenges that a single-database architecture cannot solve efficiently:

1. **Transactional Integrity vs. Write Throughput:** Order placement requires atomic multi-table writes with inventory validation — a relational strength. Simultaneously, every page view and cart hover generates an event that must be logged without blocking the user — a NoSQL strength.
2. **Cross-System Visibility:** Fraud detection requires correlating real-time session behaviour (e.g., 15 cart additions in 30 seconds) with historical transaction patterns. These datasets live in separate systems.
3. **Analytics Flexibility:** Customer segmentation (RFM), product affinity (market basket), and conversion funnels each demand different query patterns — some are naturally relational (JOINs, CTEs), others are naturally document-oriented (nested arrays, aggregations).

### 1.3 Objectives

| # | Objective | Measurable Outcome |
|---|-----------|-------------------|
| O1 | Design a normalised PostgreSQL schema with ≥3 tables and multiple relationship types | 7 tables: `users`, `customers`, `products`, `orders`, `order_items`, `outbox`, `alerts` + `order_audit_log` |
| O2 | Implement 4 database triggers demonstrating advanced SQL | Stock validation, inventory deduction, CDC outbox, audit logging |
| O3 | Design MongoDB collections using recognised NoSQL patterns | Bucket Pattern (`user_sessions`), Computed Pattern (`session_stats`), CDC target (`customer_order_summary`) |
| O4 | Implement CDC synchronisation between databases | Outbox Pattern: PostgreSQL trigger → async poller → MongoDB update |
| O5 | Build complex analytical queries on both databases | RFM segmentation (CTE + NTILE), market basket (self-join), $facet funnel |
| O6 | Real-time fraud detection pipeline | MongoDB session analysis triggers PostgreSQL alert insertion |
| O7 | Functional web dashboard with login and visualisations | React + Recharts with JWT authentication |

---

## 2. System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Docker Compose Environment                      │
│                                                                    │
│  ┌──────────────────┐     REST/JWT      ┌───────────────────────┐ │
│  │  React (Vite)    │ ◄──────────────► │   FastAPI (Python)    │ │
│  │  Port 3000        │                   │   Port 8000            │ │
│  │  - Product Catalog│                   │                        │ │
│  │  - Cart & Session │                   │  ┌──────────────────┐ │ │
│  │  - Admin Dashboard│                   │  │ Auth (JWT/bcrypt)│ │ │
│  │  - Recharts viz   │                   │  ├──────────────────┤ │ │
│  └──────────────────┘                   │  │ Products API     │ │ │
│                                          │  ├──────────────────┤ │ │
│                                          │  │ Cart/Clickstream │ │ │
│                                          │  ├──────────────────┤ │ │
│                                          │  │ Orders API       │ │ │
│                                          │  ├──────────────────┤ │ │
│                                          │  │ Analytics API    │ │ │
│                                          │  └──────────────────┘ │ │
│                                          │                        │ │
│                          ┌───────────────┼────────────────┐       │ │
│                          │ SQLAlchemy    │  Motor (async) │       │ │
│                          ▼               ▼                 ▼       │ │
│               ┌──────────────────┐  ┌──────────────────────────┐ │ │
│               │ PostgreSQL 15    │  │ MongoDB 7                 │ │ │
│               │ Port 5432        │  │ Port 27017                │ │ │
│               │                  │  │                           │ │ │
│               │ Tables (7):      │  │ Collections (4):          │ │ │
│               │ • users          │  │ • user_sessions (Bucket)  │ │ │
│               │ • customers      │  │ • session_stats (Computed)│ │ │
│               │ • products       │  │ • customer_order_summary  │ │ │
│               │ • orders         │  │ • funnel_metrics (Cached) │ │ │
│               │ • order_items    │  │                           │ │ │
│               │ • outbox ◄─────────────────────────────────────│ │ │
│               │ • alerts ◄────────── fraud detection ──────────│ │ │
│               │ • order_audit_log │  │                           │ │ │
│               │                  │  │                           │ │ │
│               │ Triggers (4):    │  │ Patterns:                 │ │ │
│               │ 1. Stock check   │  │ • Bucket ($push + $inc)   │ │ │
│               │ 2. Inventory ded.│  │ • Computed (pre-agg)      │ │ │
│               │ 3. Outbox (CDC)  │  │ • CDC target (async sync) │ │ │
│               │ 4. Audit log     │  │ • TTL index (auto-expire) │ │ │
│               └──────────────────┘  └──────────────────────────┘ │ │
└──────────────────────────────────────────────────────────────────┘
```

**Data Flow Summary:**
- **Write Path:** Client → FastAPI → PostgreSQL transaction → Outbox trigger fires → Background async poller reads `outbox` → MongoDB `customer_order_summary` updated
- **Read Path (Transactions):** Client → FastAPI → PostgreSQL (orders, products, customers via SQLAlchemy ORM + raw SQL)
- **Read Path (Analytics):** Client → FastAPI → MongoDB aggregations (funnel, sessions via Motor async driver)
- **Fraud Path:** Cart API → MongoDB session check → if threshold exceeded → PostgreSQL `alerts` INSERT

**Technology Justification:**

| Choice | Rationale |
|--------|-----------|
| **PostgreSQL** over MySQL | Native UUID support, richer JSONB for outbox payload, superior CTE/window function support for RFM queries |
| **MongoDB** over Cassandra/DynamoDB | Document model naturally maps clickstream event arrays; $facet and aggregation pipeline are well-suited for funnel analytics; TTL indexes handle session expiry without application code |
| **FastAPI** over Flask/Django | Native async support (essential for Motor MongoDB driver); automatic OpenAPI/Swagger docs; Pydantic validation reduces boilerplate |
| **Outbox Pattern** over Kafka/Debezium | Avoids additional infrastructure complexity; sufficient for project scope where CDC latency ≤5 seconds is acceptable; demonstrates understanding of event-driven patterns without external dependencies |
| **Docker Compose** | One-command reproducible environment; examiners can verify all components run identically |

---

## 3. Dataset Description

### 3.1 Data Sources

The project uses a real-world e-commerce dataset containing customer profiles, product catalogues, transaction records, and user interaction logs. All files are stored in the `data/` directory and loaded via `backend/data_loader.py`.

| File | Records | Key Columns | Loaded Into |
|------|---------|-------------|-------------|
| `customers.csv` | ~13,000 | `customer_id`, `name`, `email`, `country`, `age`, `signup_date`, `marketing_opt_in` | PostgreSQL `customers` + `users` |
| `products.csv` | ~1,000 | `product_id`, `category`, `name`, `price_usd`, `cost_usd`, `margin_usd` | PostgreSQL `products` |
| `orders.csv` | ~10,000 | `order_id`, `customer_id`, `order_time`, `payment_method`, `discount_pct`, `total_usd` | PostgreSQL `orders` |
| `order_items.csv` | ~25,000 | `order_id`, `product_id`, `unit_price_usd`, `quantity`, `line_total_usd` | PostgreSQL `order_items` |
| `clickstream_events.csv` | ~100,000 | `event_id`, `session_id`, `timestamp`, `event_type`, `product_id` | MongoDB `user_sessions` |
| `sessions.csv` | ~10,000 | `session_id`, `customer_id`, `start_time`, `device`, `source`, `country` | MongoDB `user_sessions` |

### 3.2 Data Characteristics

- **Customers** span multiple countries (`JP`, `IN`, `BR`, `FR`, `PL`, `DE`) with ages ranging 18–75, providing a realistic international e-commerce base.
- **Products** cover categories including Electronics, Clothing, Home & Garden, and Books with prices ranging from $5 to $1,500 USD.
- **Orders** include payment method diversity (card, PayPal, bank transfer) and discount percentages (0–30%), reflecting real promotional scenarios.
- **Clickstream events** follow the standard e-commerce funnel: `page_view` → `add_to_cart` → `checkout` → `purchase`, with typical drop-off rates suitable for funnel analysis.
- **Session metadata** captures device type (mobile, desktop, tablet) and traffic source (organic, email, social), enabling segmented analytics.

### 3.3 Entity-Relationship Design

The full ER diagram is documented in `docs/ER_Diagram.md`. Key design decisions:

- **`customer_id` uses UUID** rather than auto-increment INTEGER to avoid enumeration attacks and support distributed systems.
- **`products.stock_quantity` has a CHECK constraint** (`>= 0`) enforced at the database level, not just application code.
- **`order_items` enforces `quantity > 0`** via CHECK constraint, preventing invalid line items at the schema level.
- **`outbox.payload` uses JSONB** for schema-flexible event storage — different event types can have different payload structures without schema migration.
- **MongoDB `user_sessions` uses the Bucket Pattern** — events are accumulated in a single document per session using `$push` + `$inc`, avoiding the document-per-event anti-pattern that causes index bloat.

---

## 4. Implementation Details & Progress

### 4.1 Completed Components (as of June 22, 2026)

| Component | Status | Implementation Summary |
|-----------|--------|----------------------|
| **PostgreSQL Schema** | ✅ | 7 tables defined in `models/relational.py` using SQLAlchemy ORM. Includes FK constraints with `ON DELETE CASCADE`, CHECK constraints on `stock_quantity` and `quantity`, and UUID primary keys for customers/orders. |
| **4 PostgreSQL Triggers** | ✅ | Defined in `triggers.sql` and auto-loaded at container startup via Docker volume mount. `trg_check_stock` (BEFORE INSERT) validates inventory; `trg_deduct_inventory` (AFTER INSERT) decrements stock; `trg_outbox_order` (AFTER INSERT) writes CDC events; `trg_audit_order` (AFTER UPDATE) logs status/amount changes to `order_audit_log`. |
| **MongoDB Collections** | ✅ | 4 collections with indexes defined in `services/nosql_service.py:init_mongo_indexes()`. Compound unique index on `(customer_id, session_id)`, TTL index on `end_time` (30-day expiry), and text indexes for search. |
| **Auth API** | ✅ | JWT-based registration and login in `api/auth.py`. Passwords hashed with bcrypt via `passlib`. Token expiry configurable via environment variable. |
| **Products API** | ✅ | Paginated catalogue with category filter and text search in `api/products.py`. Returns product ID, category, unit price, and stock quantity. |
| **Cart/Clickstream API** | ✅ | `api/cart.py` POST `/event` records actions in MongoDB using the Bucket Pattern. Each `add_to_cart` triggers a fraud check comparing recent event velocity against configurable thresholds. |
| **Orders API** | ✅ | `api/orders.py` creates orders in a PostgreSQL transaction. Validates stock before committing; triggers handle inventory deduction and outbox population automatically. |
| **Analytics API** | ✅ | `api/analytics.py` exposes 8 endpoints: RFM segmentation, market basket pairs, funnel metrics, cart abandonment, audit trail, fraud alerts, top products, and sales by category. Admin-only endpoints protected by role check. |
| **CDC / Outbox Processor** | ✅ | `services/sync_service.py` runs an async background task polling the `outbox` table every 5 seconds. Processes `order_created` events by updating `customer_order_summary` in MongoDB with `$inc` on `total_orders` and `total_spent`. |
| **Data Loader** | ✅ | `data_loader.py` ingests all 6 CSV files. Creates both `Customer` and `User` records (for JWT auth), maps CSV customer IDs to UUIDs, and loads clickstream events into MongoDB sessions. |
| **Benchmark Suite** | ✅ | `benchmark/benchmark_runner.py` measures: (1) MongoDB bulk insert throughput, (2) PostgreSQL concurrent UPDATE contention, (3) 5-table JOIN query performance, (4) MongoDB aggregation pipeline speed. Generates `benchmark_results.png` via matplotlib. |
| **React Frontend** | ✅ | 4 functional components in `frontend/src/components/`: `Login.jsx` (JWT auth), `ProductList.jsx` (catalogue with search/filter/pagination), `Cart.jsx` (clickstream event recording + fraud trigger demo), `AdminDashboard.jsx` (Recharts visualisations for RFM, funnel, alerts, market basket). |
| **Docker Compose** | ✅ | `docker-compose.yml` orchestrates 4 services: PostgreSQL 15, MongoDB 7, FastAPI backend, and React/Vite frontend. Health checks ensure startup ordering. Triggers auto-loaded via `docker-entrypoint-initdb.d`. |

### 4.2 Team Roles & Contributions

| Member | Primary Responsibility | Key Files |
|--------|----------------------|-----------|
| Tan Ding Mao (Lead) | Backend architecture, PostgreSQL schema, triggers, CDC/Outbox, Docker setup, report writing | `main.py`, `config.py`, `models/relational.py`, `triggers.sql`, `services/sync_service.py`, `docker-compose.yml` |
| [Member 2] | MongoDB schema, Bucket/Computed patterns, fraud detection, benchmark suite | `models/nosql_schemas.py`, `services/nosql_service.py`, `benchmark/benchmark_runner.py` |
| [Member 3] | API routes, data loader, complex SQL queries (RFM, market basket) | `api/*.py`, `data_loader.py`, `services/relational_service.py` |
| [Member 4] | React frontend, Recharts integration, CSS styling, presentation slides | `frontend/src/**`, `api.js`, `*.css` |

> **Note:** All members contributed to code review, integration testing, and documentation. Equal contribution structure qualifies for the 5% team mark increase.

---

## 5. Challenges, Risks & Mitigation

| Risk | Impact | Mitigation Strategy |
|------|--------|---------------------|
| **Cross-DB consistency failure** | MongoDB `customer_order_summary` drifts from PostgreSQL ground truth | Outbox processor retries unprocessed events on next poll cycle; `total_orders` uses `$inc` (idempotent if duplicate) |
| **PostgreSQL trigger failure blocks orders** | `trg_check_stock` raising exception rolls back the entire transaction | Application-level stock validation in `orders.py:create_order()` as defence-in-depth before trigger fires |
| **MongoDB connection drops** | Clickstream events lost, fraud detection unavailable | `get_mongo_db()` lazy-initialises on first call; connection errors surface as HTTP 500 with clear messaging |
| **Large CSV ingestion timeout** | Data loader OOM or exceeds Docker memory limits | Batch commits every 500–1,000 rows; products skip duplicates by `product_id` |
| **Fraud detection false positives** | Legitimate rapid shopping flagged as fraud | Threshold is configurable via `FRAUD_EVENT_THRESHOLD` env var; alerts are non-blocking (logged, not rejected) |

---

## 6. Testing Strategy (Next Phase)

| Test Type | Approach | Success Criteria |
|-----------|----------|-----------------|
| **Unit Tests** | Pytest for service functions (`compute_rfm_segmentation`, `check_fraud_alert`) | All functions return expected output shapes |
| **Integration Tests** | Docker Compose + HTTPX against running API | 201 on order creation, 200 on product list, 401 on unauthenticated access |
| **Trigger Verification** | Manual SQL: INSERT order_item, verify `stock_quantity` decremented, verify `outbox` row created | PostgreSQL state matches expected after each operation |
| **CDC Verification** | Create order via API → wait 10s → query MongoDB `customer_order_summary` | `total_orders` incremented, `total_spent` reflects order amount |
| **Fraud Scenario** | Rapid-fire 15 `add_to_cart` events via API → check `/api/analytics/alerts` | Alert appears within 1 request cycle |

---

## 7. Timeline & Remaining Work

```
Phase 1 (May 26 – Jun 8):  ✅ Schema design, ERD, dataset analysis, Docker setup
Phase 2 (Jun 9  – Jun 22): ✅ Backend API, triggers, CDC, data loader, frontend, progress report
Phase 3 (Jun 23 – Jul 6):  🔲 Integration testing, trigger verification, CDC validation,
                              fraud scenario testing, benchmark tuning, bug fixes
Phase 4 (Jul 7  – Jul 13): 🔲 Final report writing, slide deck preparation, 10-minute
                              video recording with all members presenting
Phase 5 (Jul 14 – Jul 17): 🔲 Peer review submission (online form)
```

**Key milestones remaining:**
- Execute all 5 integration test scenarios (Section 6)
- Tune benchmark parameters for meaningful comparison charts
- Record video demo showing trigger execution, CDC sync, and fraud detection in real-time
- Polish final report with actual benchmark results and screenshots

---

*End of Progress Report*
