# G11 — Progress Report
### INF2003 Group Project &middot; E-Commerce Clickstream & Transaction Analytics
### Team Hanzalians

<div align="right"><sub>`G11_Progress Report.pdf` &middot; Max 4 pages (excl. cover)</sub></div>

---

## Cover Page

| | |
|---|---|
| **Module** | INF2003 Database Design & Implementation |
| **Group ID** | G11 &middot; Team Hanzalians |
| **Project** | E-Commerce Clickstream & Transaction Analytics |
| **Topic** | Topic 2 — Dual-Database Analytics Platform |
| **Members** | Hanzalah Hisam (Team Lead), Faris Zharfan, Lucas Leow, Muhammad Hasan Bin Suwandi, Muhammad Raees Irfan Bin Ishak, Muhammad 'Afif Bin Muhd Lotfi Jarhom |
| **Lead Contact** | [lead-email@sit.singaporetech.edu.sg] |
| **Submitted** | 22 June 2026 |

---

## 1. Application Background & Problem Statement

### 1.1 Background

Modern e-commerce platforms generate massive volumes of data every second. This data falls into two fundamentally opposing categories: highly **structured financial transactions** (purchases, payments, inventory) demanding strict **ACID** guarantees (Atomicity, Consistency, Isolation, Durability), and high-velocity, semi-structured **behavioural logs** (page views, cart actions, session flows) best served by **BASE** (Basically Available, Soft-state, Eventually consistent) systems that prioritise write throughput over immediate consistency.

Attempting to process both within a single database creates significant performance bottlenecks. Relational databases struggle to scale with the chaotic influx of clickstream data, while NoSQL systems lack the transactional rigour required for monetary processing and inventory management. A **polyglot persistence** approach — intelligently routing each data shape to the database optimised for it — resolves this impedance mismatch directly. This project builds a mock e-commerce storefront that decouples user browsing behaviour from purchase execution, demonstrating an optimised dual-database architecture capable of identifying complex consumer patterns (cart abandonment, RFM segments, conversion funnels) without sacrificing system stability.

### 1.2 Problem Statement

Online retailers face three interconnected challenges unsolvable by a single-database architecture:

1. **Transactional Integrity vs. Write Throughput** — Order placement requires atomic multi-table writes with inventory validation (a relational strength). Simultaneously, every page view and cart action must be logged without blocking the user experience (a NoSQL strength).
2. **Cross-System Visibility** — Fraud detection demands correlating real-time session behaviour (e.g., 15 cart additions in 30 seconds) with historical transaction patterns residing in separate database systems.
3. **Analytics Flexibility** — Customer segmentation (RFM), product affinity (market basket), and conversion funnels each demand different query paradigms: some are naturally relational (JOINs, CTEs), others are document-oriented (nested arrays, aggregations).

### 1.3 Objectives

| # | Objective | Measurable Deliverable |
|---|-----------|----------------------|
| O1 | Design normalised PostgreSQL schema (≥3 tables, multiple relationship types) | 7 tables: `users`, `customers`, `products`, `orders`, `order_items`, `outbox`, `alerts` + `order_audit_log` |
| O2 | Implement advanced SQL via 4 database triggers | Stock validation, inventory deduction, CDC outbox, audit logging — auto-deployed at container start |
| O3 | Design MongoDB collections using established NoSQL patterns | Bucket Pattern (`user_sessions`), Computed Pattern (`session_stats`), CDC target (`customer_order_summary`) |
| O4 | Achieve cross-database synchronisation | Outbox Pattern: PostgreSQL trigger → async poller → MongoDB `$inc` update |
| O5 | Build complex analytical queries on both databases | RFM segmentation (CTE + NTILE), market basket (self-join), $facet funnel analysis |
| O6 | Implement real-time fraud detection pipeline | MongoDB session velocity analysis triggers PostgreSQL `alerts` insertion |
| O7 | Deliver functional web dashboard with JWT authentication | React + Recharts: product catalogue, cart, admin analytics (RFM, funnel, alerts, basket) |

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Docker Compose Environment                      │
│                                                                   │
│  ┌──────────────────┐    REST/JWT     ┌────────────────────────┐ │
│  │  React (Vite)    │◄──────────────►│   FastAPI (Python)     │ │
│  │  :3000            │                │   :8000                 │ │
│  │  Catalog │ Cart   │                │  Auth │ Products       │ │
│  │  Admin  │ Charts  │                │  Cart │ Orders │ Stats │ │
│  └──────────────────┘                └───────┬───────┬────────┘ │
│                                              │       │          │
│                              SQLAlchemy (ORM)│       │Motor     │
│                                              ▼       ▼          │
│  ┌──────────────────────┐       ┌─────────────────────────────┐ │
│  │  PostgreSQL 15 :5432 │       │  MongoDB 7 :27017            │ │
│  │                      │       │                              │ │
│  │  Tables:             │  CDC  │  Collections:                │ │
│  │  users, customers,   │──────►│  user_sessions (Bucket)     │ │
│  │  products, orders,   │outbox │  session_stats (Computed)   │ │
│  │  order_items, outbox,│       │  customer_order_summary     │ │
│  │  alerts, audit_log   │       │  funnel_metrics (Cached)    │ │
│  │                      │       │                              │ │
│  │  Triggers:           │ fraud │  Patterns:                   │ │
│  │  stock check, inv.ded│◄──────│  $push+$inc │ $facet │ TTL  │ │
│  │  outbox CDC, audit   │       │                              │ │
│  └──────────────────────┘       └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Data Flow & Routing Logic:**
- **Browsing (Write-heavy):** Client → FastAPI → MongoDB `user_sessions` — continuous `$push` + `$inc` via Bucket Pattern; near O(1) insert complexity
- **Purchasing (ACID):** Client → FastAPI → PostgreSQL transaction → triggers fire (stock check → inventory deduction → outbox CDC)
- **CDC Bridge:** Outbox trigger writes event → async background poller reads `outbox` → MongoDB `customer_order_summary` synchronised
- **Fraud Detection:** Cart API → MongoDB session velocity check → if threshold exceeded → PostgreSQL `alerts` INSERT

**Algorithmic Efficiency:** This decoupled architecture is designed for optimal performance. By routing unstructured click logs to MongoDB, we achieve near O(1) time complexity for continuous event insertion via the Bucket Pattern. Complex analytical operations — such as multi-table JOINs for RFM segmentation and market basket co-occurrence — are reserved exclusively for PostgreSQL, whose optimised query planner handles these resource-intensive operations efficiently without competing with high-velocity write traffic.

**Technology Justification:**

| Choice | Rationale |
|--------|-----------|
| **PostgreSQL** over MySQL | Native UUID type, JSONB for flexible outbox payloads, superior CTE and window function support essential for RFM queries |
| **MongoDB** over Cassandra/DynamoDB | Document model naturally maps clickstream event arrays; $facet aggregation pipeline ideal for multi-stage funnel analysis; TTL indexes auto-expire stale sessions |
| **FastAPI** over Flask/Django | Native async I/O (essential for Motor MongoDB driver); automatic OpenAPI/Swagger documentation; Pydantic request validation reduces boilerplate |
| **Outbox Pattern** over Kafka/Debezium | Avoids external infrastructure complexity; CDC latency ≤5 seconds is acceptable for project scope; demonstrates event-driven architectural thinking |
| **Docker Compose** | One-command reproducible environment ensures examiners can verify all components identically |

---

## 3. Dataset Description

### 3.1 Data Sources

The project utilises real-world e-commerce datasets sourced from Kaggle [1][2]. All files reside in `data/` and are ingested via `backend/data_loader.py`.

| File | ~Records | Representative Columns | Target Database |
|------|----------|------------------------|-----------------|
| `customers.csv` | 13,000 | `customer_id`, `name`, `email`, `country`, `age`, `signup_date`, `marketing_opt_in` | PostgreSQL `customers` + `users` |
| `products.csv` | 1,000 | `product_id`, `category`, `price_usd`, `cost_usd`, `margin_usd` | PostgreSQL `products` |
| `orders.csv` | 10,000 | `order_id`, `customer_id`, `order_time`, `payment_method`, `discount_pct`, `total_usd` | PostgreSQL `orders` |
| `order_items.csv` | 25,000 | `order_id`, `product_id`, `unit_price_usd`, `quantity`, `line_total_usd` | PostgreSQL `order_items` |
| `clickstream_events.csv` | 100,000 | `event_id`, `session_id`, `timestamp`, `event_type`, `product_id` | MongoDB `user_sessions` |
| `sessions.csv` | 10,000 | `session_id`, `customer_id`, `start_time`, `device`, `source`, `country` | MongoDB `user_sessions` |

### 3.2 Data Profile

- **Customers:** Multi-country distribution (`JP`, `IN`, `BR`, `FR`, `PL`, `DE`), age range 18–75 — provides a realistic international e-commerce user base for segmentation.
- **Products:** Categories spanning Electronics, Clothing, Home & Garden, and Books; prices ranging $5–$1,500 USD with cost and margin data for profitability analysis.
- **Orders:** Payment method diversity (card, PayPal, bank transfer), discount percentages 0–30% — reflects real promotional pricing dynamics.
- **Clickstream:** Complete e-commerce funnel — `page_view` → `add_to_cart` → `checkout` → `purchase` — with natural drop-off rates ideal for conversion analysis.
- **Sessions:** Device diversity (mobile, desktop, tablet) and traffic sources (organic, email, social) enabling segmented behavioural analytics.

### 3.3 Entity-Relationship Design

The complete ER diagram is documented in `docs/ER_Diagram.md`. Critical schema decisions:

- **UUID primary keys** on `customers` and `orders` — prevents enumeration attacks, supports future distributed deployment.
- **`CHECK (stock_quantity >= 0)`** on `products` — referential integrity enforced at database level, not application code.
- **`CHECK (quantity > 0)`** on `order_items` — invalid line items rejected by the schema before any trigger executes.
- **JSONB `outbox.payload`** — schema-flexible event storage enabling heterogeneous event types without migration.
- **MongoDB Bucket Pattern** — all events from a single session accumulated in one document via `$push` + `$inc`, avoiding the document-per-event anti-pattern that causes exponential index growth in high-throughput systems.

---

## 4. Implementation Progress (as of 22 June 2026)

### 4.1 Completed Components

| Component | File(s) | Summary |
|-----------|---------|---------|
| **PostgreSQL Schema** | `models/relational.py` | 7 tables with FK `ON DELETE CASCADE`, CHECK constraints, UUID PKs for customers and orders |
| **4 SQL Triggers** | `triggers.sql` | Stock check (BEFORE INSERT), inventory deduction (AFTER INSERT), outbox CDC (AFTER INSERT), audit log (AFTER UPDATE) — auto-loaded via `docker-entrypoint-initdb.d` |
| **MongoDB Collections** | `services/nosql_service.py` | 4 collections with compound unique index, TTL index (30-day auto-expiry), text indexes for search |
| **JWT Auth API** | `api/auth.py` | Registration & login with bcrypt password hashing; configurable token expiry via environment variable |
| **Products API** | `api/products.py` | Paginated catalogue with category filter, text search, and stock visibility |
| **Cart/Clickstream API** | `api/cart.py` | Bucket Pattern event recording; fraud velocity check triggered on every `add_to_cart` action |
| **Orders API** | `api/orders.py` | ACID transaction with pre-commit stock validation; PostgreSQL triggers handle inventory deduction and outbox CDC automatically |
| **Analytics API** | `api/analytics.py` | 8 endpoints: RFM segmentation, market basket pairs, funnel metrics, cart abandonment, audit trail, fraud alerts, top products, sales by category — admin endpoints role-protected |
| **CDC Sync Processor** | `services/sync_service.py` | Async background poller (5 s interval) processes `outbox` table, updates MongoDB `customer_order_summary` via `$inc` on `total_orders` and `total_spent` |
| **Data Loader** | `data_loader.py` | Ingests all 6 CSV datasets; creates linked `Customer` + `User` records for JWT authentication; maps CSV integer IDs to PostgreSQL UUIDs |
| **Benchmark Suite** | `benchmark/benchmark_runner.py` | 4 performance tests: MongoDB bulk insert, PostgreSQL concurrent hotspot UPDATEs, 5-table JOIN query, MongoDB aggregation pipeline; outputs `benchmark_results.png` via matplotlib |
| **React Frontend** | `frontend/src/components/` | 4 functional views: `Login` (JWT), `ProductList` (search/filter/paginate), `Cart` (clickstream + fraud trigger demo), `AdminDashboard` (Recharts: RFM pie, funnel bar, alerts table, market basket) |
| **Docker Compose** | `docker-compose.yml` | 4-container orchestration (PostgreSQL 15, MongoDB 7, FastAPI backend, Vite frontend) with health checks ensuring correct startup ordering |

### 4.2 Team Roles & Contributions

| Member | Primary Responsibility | Key Deliverables |
|--------|----------------------|-----------------|
| **Hanzalah Hisam** (Lead) | System architecture, PostgreSQL schema design, Docker orchestration, progress report | `main.py`, `config.py`, `docker-compose.yml`, `models/relational.py`, report writing |
| **Faris Zharfan** | API routes, JWT authentication, complex SQL queries (RFM, market basket) | `api/auth.py`, `api/orders.py`, `api/analytics.py`, `services/relational_service.py` |
| **Lucas Leow** | MongoDB schema design, Bucket & Computed patterns, fraud detection engine | `models/nosql_schemas.py`, `services/nosql_service.py`, `api/cart.py` |
| **Muhammad Hasan** | CDC/Outbox processor, data loader, cross-database integration testing | `services/sync_service.py`, `data_loader.py`, CDC verification test cases |
| **Muhammad Raees Irfan** | React frontend, Recharts visualisations, CSS styling, API client | `frontend/src/**`, `api.js`, `AdminDashboard.jsx` with all chart components |
| **Muhammad 'Afif** | PostgreSQL triggers, benchmark suite, presentation slides, video recording | `triggers.sql`, `benchmark/benchmark_runner.py`, slide deck, demo video |

> All members contributed to code review, integration testing, and documentation. Equal contribution across all six members qualifies the team for the 5% mark increase.

---

## 5. Risk Register & Mitigation

| Risk | Impact | Mitigation Strategy |
|------|--------|---------------------|
| **Cross-DB consistency drift** | MongoDB `customer_order_summary` diverges from PostgreSQL source of truth | Outbox processor retries unprocessed events each poll cycle; `$inc` operations are idempotent on replay |
| **Trigger failure blocks legitimate orders** | `trg_check_stock` exception rolls back entire transaction, rejecting valid purchases | Application-level stock validation in `orders.py:create_order()` as defence-in-depth before the trigger fires |
| **MongoDB connection loss** | Clickstream events lost; fraud detection unavailable | Lazy-initialised connection via `get_mongo_db()`; connection errors surface as HTTP 500 with clear diagnostic messaging |
| **CSV ingestion memory overflow** | Data loader exceeds Docker container memory during bulk import | Batch commits every 500–1,000 rows with intermediate `db.commit()` calls; duplicate products skipped by `product_id` check |
| **Fraud detection false positives** | Legitimate rapid shopping (e.g., holiday gift buying) incorrectly flagged | `FRAUD_EVENT_THRESHOLD` configurable via environment variable; alerts are non-blocking (logged, not rejected) |

---

## 6. Testing Strategy (Phase 3 — 23 Jun to 6 Jul)

| Test Type | Method | Success Criteria |
|-----------|--------|------------------|
| **Unit Tests** | Pytest on core service functions (`compute_rfm_segmentation`, `check_fraud_alert`) | All functions return expected output shapes; edge cases (zero orders, null sessions) handled |
| **Integration Tests** | HTTPX against running Docker Compose API | `201` on order POST; `200` on product GET with pagination; `401` on unauthenticated routes |
| **Trigger Verification** | Manual SQL: INSERT `order_item` → query `products.stock_quantity` and `outbox` table | Stock correctly decremented; outbox row created with matching `order_id`, `customer_id`, and `total_amount` |
| **CDC End-to-End** | Create order via API → wait 10 seconds → query MongoDB `customer_order_summary` | `total_orders` incremented; `total_spent` accurately reflects order amount; `last_updated` timestamp within 10 s of order |
| **Fraud Scenario** | Rapid-fire 15 `add_to_cart` events via API → `GET /api/analytics/alerts` | Alert appears within 1 request cycle; session document in MongoDB has `flagged: true` |

---

## 7. Timeline & Remaining Work

```
✅ Phase 1 (26 May – 8 Jun)    Dataset finalisation, ER diagram, MongoDB schema design,
                               Docker environment setup, technology evaluation
✅ Phase 2 (9 Jun – 22 Jun)    Database initialisation, CSV data import, CRUD operations
                               on both databases, mock storefront, API routing logic,
                               customer_id bridging between SQL and NoSQL, progress report
🔲 Phase 3 (23 Jun – 6 Jul)    Advanced SQL (complex JOINs, CTEs), NoSQL aggregation
                               pipelines, trigger & CDC validation, fraud scenario testing,
                               benchmark tuning, bug fixes
🔲 Phase 4 (7 Jul – 13 Jul)    Final report drafting, slide deck preparation, 10-minute
                               video recording (all six members presenting), source code
                               packaging into single ZIP
🔲 Phase 5 (14 Jul – 17 Jul)   Peer review submission via online form
```

**Remaining Milestones:** Execute 5 integration test scenarios (Section 6) → tune benchmark parameters for meaningful performance comparison charts → record video demonstration showing live trigger execution, CDC synchronisation, and fraud alert triggering → finalise report with actual benchmark graphs and application screenshots.

---

## References

[1] Waqi. "E-commerce Clickstream and Transaction Dataset." *Kaggle*. Available: https://www.kaggle.com/datasets/waqi786/e-commerce-clickstream-and-transaction-dataset

[2] Wafaa Elhusseini. "Synthetic E-commerce Transactions + Clickstream 2020–2025." *Kaggle*. Available: https://www.kaggle.com/datasets/wafaaelhusseini/e-commerce-transactions-clickstream

---

*End of Progress Report — INF2003 Group 11 (Team Hanzalians)*
