# 🤝 Technical Work Distribution — INF2003 Group 11

**Team Hanzalians · 6 Members · Equal Weightage**

> Planning, architecture decisions, and design choices were discussed collaboratively by the entire team. This document outlines individual technical implementation contributions only.

---

## 1. Hanzalah Hisam — *Team Lead*

### Files Owned

| File | Lines | What It Does |
|------|-------|-------------|
| `docker-compose.yml` | ~120 | 5-container orchestration: PostgreSQL, MongoDB, Backend, Frontend, Data Loader. Health checks, volume mounts, environment config, one-shot reset service |
| `backend/main.py` | ~100 | FastAPI entry point, lifespan hooks (table creation, MongoDB indexes, outbox processor start/stop), CORS middleware, 5 router registrations |
| `backend/config.py` | ~40 | Centralized settings from environment variables: DB URLs, JWT config, fraud thresholds, outbox interval |
| `backend/models/relational.py` | ~200 | SQLAlchemy ORM — 8 table classes (users, customers, products, orders, order_items, outbox, order_audit_log, alerts), portable UUID/JSONB types, FK relationships, CHECK constraints |
| `backend/.dockerignore` | — | Docker build optimization |

### Technical Contributions
- **Docker orchestration** — all containers communicate over internal Docker network, health checks ensure correct startup order
- **Schema design** — UUID PKs (anti-enumeration), CHECK constraints at DB level, ON DELETE CASCADE, composite indexes
- **Config management** — environment-variable-driven settings with sensible defaults, supports local dev and Docker
- **CORS setup** — configured for frontend (localhost:3000) connectivity

---

## 2. Faris Zharfan — *Backend API & Complex SQL*

### Files Owned

| File | Lines | What It Does |
|------|-------|-------------|
| `backend/api/auth.py` | ~200 | JWT registration/login with bcrypt hashing, `get_current_user` token decoder, `get_admin_user` role guard, OAuth2 password flow, user input validation |
| `backend/api/orders.py` | ~120 | Order creation in ACID transaction — validates products exist and stock is sufficient, computes totals, creates Order + OrderItems, commits atomically |
| `backend/api/analytics.py` | ~100 | 9 analytics endpoints: RFM, market basket, funnel, cart abandonment, alerts, audit trail, top products, sales by category. Admin-only endpoints use `get_admin_user` dependency |
| `backend/api/products.py` | ~80 | Paginated catalog with category ILIKE filter, text search, single product lookup, distinct categories |
| `backend/services/relational_service.py` | ~250 | **RFM Segmentation** — CTE + NTILE(4) classifying 32k customers into Champions/Loyal/Potential Loyalists/At Risk/Lost. **Market Basket** — self-join on order_items for product co-occurrence pairs. **Audit Trail** — order change history queries. **Top Products** — GROUP BY with aggregation. **Alerts** — recent fraud alert retrieval |

### Technical Contributions
- **Advanced SQL** — CTEs, window functions (NTILE), self-joins, complex aggregations
- **JWT security** — `python-jose` with HS256, `sub` claim as string (bug discovered & fixed), role-based access control
- **Input validation** — Pydantic models on every endpoint, proper HTTP error codes (400/401/403/404/422)

---

## 3. Lucas Leow — *MongoDB & NoSQL Engine*

### Files Owned

| File | Lines | What It Does |
|------|-------|-------------|
| `backend/models/nosql_schemas.py` | ~80 | Pydantic models: `ActionType` enum (page_view/add_to_cart/checkout/purchase), `ClickstreamEvent`, `UserSession` with Bucket Pattern structure |
| `backend/services/nosql_service.py` | ~370 | **Bucket Pattern** — `track_clickstream_event()` with `updateOne({$push + $inc + $set + $setOnInsert}, upsert)`. **Fraud Detection** — `check_fraud_alert()` counting events in time window, setting `flagged` on threshold breach. **Funnel Analytics** — `compute_funnel_metrics()` using MongoDB `$facet` pipeline (4 parallel aggregations). **Cart Abandonment** — `detect_cart_abandonment()` finding sessions with add_to_cart but no checkout. **CDC Target** — `update_customer_order_summary()` with atomic `$inc` on total_orders and total_spent. **Indexes** — `init_mongo_indexes()`: compound unique, TTL (30-day), flagged, nested timestamp |
| `backend/api/cart.py` | ~100 | Clickstream event recording endpoint, session retrieval, fraud check integration on every add_to_cart, action_type validation |

### Technical Contributions
- **4 NoSQL design patterns** — Bucket (events per session), Computed (pre-aggregated stats), CDC Target (denormalized order view), Cached (funnel results)
- **$facet aggregation** — single pipeline computing 4 conversion stages in parallel
- **Cross-DB fraud pipeline** — MongoDB velocity analysis → PostgreSQL alert insertion
- **TTL index** — automatic 30-day session expiry via MongoDB's native TTL mechanism

---

## 4. Muhammad Hasan Bin Suwandi — *CDC, Data Pipeline & Integration*

### Files Owned

| File | Lines | What It Does |
|------|-------|-------------|
| `backend/services/sync_service.py` | ~130 | **Outbox Processor** — async background task polling PostgreSQL `outbox` table every 5s, processes `order_created` events, marks `processed = true`, syncs to MongoDB via `$inc`. Thread executor for non-blocking DB queries. Graceful startup/shutdown |
| `backend/data_loader.py` | ~250 | CSV ingestion pipeline: reads 6 files, creates Customer + User records (20k each), UUID mapping from CSV integers, batch commits every 1000 rows, clickstream events loaded into MongoDB, bcrypt password generation via passlib |
| `backend/reset_db.py` | ~80 | Database wipe utility: drops all 8 PostgreSQL tables in FK-safe order, recreates from ORM, re-applies triggers, drops all 4 MongoDB collections, re-initializes indexes |
| `backend/tests/test_suite.py` | ~800 | 161 automated tests — 10 sections covering health, auth, products, cart, orders, analytics, admin, triggers, MongoDB, error handling |

### Technical Contributions
- **CDC / Outbox Pattern** — at-least-once delivery guarantee, idempotent `$inc` operations, retry on failure
- **Data pipeline** — 275k rows ingested across 6 CSVs into two different database types
- **Integration verification** — order → trigger → outbox → poller → MongoDB sync verified end-to-end
- **Bug fixes** — hardcoded bcrypt hash replacement with passlib runtime generation (fixed 20k user passwords)
- **Frontend cleanup** — removed dead code from Cart.jsx and Login.jsx

---

## 5. Muhammad Raees Irfan Bin Ishak — *Frontend & UX Engineering*

### Files Owned

| File | Lines | What It Does |
|------|-------|-------------|
| `frontend/src/App.jsx` | ~160 | React SPA root — BrowserRouter, JWT auth state, shared cart state with localStorage persistence, `addToCart`/`removeFromCart`/`updateCartQuantity`/`clearCart` functions, cart badge counter in navbar, role-based navigation |
| `frontend/src/components/ProductList.jsx` | ~200 | Product catalog — 7 category icons (⚡👗💄📚🏠⚽🎮), stock color coding (green/orange/red), in-cart green badge overlay, search + category filter + pagination, toast notifications |
| `frontend/src/components/Cart.jsx` | ~230 | Shopping cart — full table (Product/Category/Price/Qty/Total/Remove), ± quantity buttons with stock limit guard, subtotal row, Place Order button (triggers ACID transaction), Clear Cart, Continue Shopping, clickstream debug panel in collapsible `<details>` |
| `frontend/src/components/Login.jsx` | ~130 | Auth forms — "Welcome Back"/"Create Account" with subtitles, input placeholders, demo credentials card (user_1/password123), error display, loading state |
| `frontend/src/components/AdminDashboard.jsx` | ~250 | Analytics dashboard — stat cards (Customers/Page Views/Alerts/Pairs), pill-style tabs with icons, RFM pie chart (Recharts PieChart), funnel bar chart (Recharts BarChart), alerts table, top products, market basket, loading spinners |
| `frontend/src/api.js` | ~90 | Axios HTTP client — base URL config, auth token header injection, all API endpoint wrappers (auth, products, cart, orders, analytics) |
| `frontend/src/index.css` | ~520 | Design system — CSS custom properties (20+ variables), gradient backgrounds, product card hover animations (lift + top border reveal), toast slide-in animations, gradient buttons with shadows, sticky navbar, responsive breakpoints (768px/480px), stat cards, pill tabs, loading spinners |

### Technical Contributions
- **Cart system** — full state management with localStorage persistence, quantity controls, stock limit enforcement
- **UX polish** — toast notification system, category-based icons, stock color coding, cart badge counter, disabled button states
- **Admin visualization** — Recharts integration (PieChart + BarChart), real-time data from 6 API endpoints
- **Responsive design** — mobile-friendly grid layouts, flex-wrap navigation

---

## 6. Muhammad 'Afif Bin Muhd Lotfi Jarhom — *Triggers, Benchmarks & Documentation*

### Files Owned

| File | Lines | What It Does |
|------|-------|-------------|
| `backend/triggers.sql` | ~180 | 4 PostgreSQL triggers — `trg_check_stock` (BEFORE INSERT, raises exception if insufficient), `trg_deduct_inventory` (AFTER INSERT, atomic decrement), `trg_outbox_order` (AFTER INSERT, JSONB event to outbox), `trg_audit_order` (AFTER UPDATE, logs old→new values). Table DDL with CHECK constraints. Auto-deploys via docker-entrypoint-initdb.d |
| `backend/benchmark/benchmark_runner.py` | ~200 | Performance suite — 4 benchmarks: MongoDB bulk insert (10k events, Bucket Pattern), PostgreSQL hotspot UPDATE (200 concurrent txns), PostgreSQL 5-table JOIN, MongoDB aggregation pipeline. Timed with Python's `time` module, results plotted via matplotlib |
| `docs/ER_Diagram.md` | ~300 | Complete database design documentation — all 8 PostgreSQL tables with column-level detail, all 4 MongoDB collections with JSON schemas, 7 indexes, 4 design pattern justifications, CDC flow diagram, data volume table (275k rows) |
| `docs/ER_Diagram.png` | generated | 9600×5400px ER diagram at 300 DPI — visual with table boxes, FK arrows (blue), trigger arrows (orange), CDC flow (purple), legend, pattern descriptions |
| `docs/generate_erd.py` | ~250 | matplotlib script that renders the ER diagram programmatically — FancyBboxPatch tables, annotation arrows, color-coded sections |
| `docs/G11_Final_Report.md` | ~300 | 8-page academic report — introduction, architecture, schema, triggers, NoSQL design, application, performance, testing (161 tests), constraints, discussion, GenAI reflection |
| `docs/generate_docx.py` | ~580 | python-docx script converting final report to professionally formatted Word document — cover page, styled headings, tables with alternating rows, embedded ER diagram image, page layout |
| `walkthrough.md` | ~550 | Non-technical guide — plain-English explanations, analogies, glossary (25+ terms), FAQ, step-by-step startup |
| `demoguide.md` | ~250 | Demo script — 8 demo sections with exact "what to say" scripts, 5-minute condensed flow, credential reference card |
| `DOCKER_TROUBLESHOOTING.md` | ~250 | Docker debugging guide — 12 common problems with diagnostic commands and fixes |

### Technical Contributions
- **4 database triggers** — complete inventory management and CDC at the database level, zero application code needed
- **Performance analysis** — quantitative comparison proving MongoDB excels at writes while PostgreSQL handles transactions and complex JOINs
- **Documentation** — comprehensive suite covering technical (README, ER Diagram), non-technical (walkthrough), operational (Docker troubleshooting), and academic (Final Report, demo guide)

---

## Summary Matrix

| Member | Primary Files | Key Tech |
|--------|-------------|----------|
| **Hanzalah** | `docker-compose.yml`, `main.py`, `config.py`, `models/relational.py` | Docker, SQLAlchemy ORM, Schema |
| **Faris** | `api/auth.py`, `api/orders.py`, `api/analytics.py`, `services/relational_service.py` | JWT, CTE/NTILE, Self-join, REST |
| **Lucas** | `services/nosql_service.py`, `models/nosql_schemas.py`, `api/cart.py` | Bucket Pattern, $facet, Fraud |
| **Hasan** | `services/sync_service.py`, `data_loader.py`, `tests/test_suite.py` | CDC, Outbox, Data Pipeline |
| **Raees** | `App.jsx`, `ProductList.jsx`, `Cart.jsx`, `Login.jsx`, `AdminDashboard.jsx`, `index.css` | React, Recharts, Cart State |
| **'Afif** | `triggers.sql`, `benchmark/`, `docs/*`, `walkthrough.md` | Triggers, Benchmarks, Docs |

---

*INF2003 Group 11 — Team Hanzalians — June 2026*


---

## Mark Allocation Overview

| Component | Weight | Evaluated Via |
|-----------|--------|---------------|
| Proposal & Progress Report | **10%** | Progress Report |
| Presentation | **15%** | Video (all members) |
| Database Design & Implementation | **40%** | Code + Report + Presentation |
| Application | **20%** | Code + Report + Presentation |
| Writing | **15%** | Final Report |

---

## Member Contributions

### 1. Hanzalah Hisam — *Team Lead*

**Focus:** System Architecture, Docker Orchestration, Progress Report

| Deliverable | Details |
|-------------|---------|
| **System Architecture** | Designed the dual-database architecture (PostgreSQL + MongoDB), Docker Compose 5-container orchestration with health checks, auto data loading, database reset |
| **PostgreSQL Schema** | SQLAlchemy ORM models for all 8 tables, CHECK constraints, UUID PKs, FK relationships |
| **Configuration** | `config.py`, `docker-compose.yml`, environment-based settings for all services |
| **Progress Report** | Authored the 4-page Progress Report (Proposal section: background, problem statement, objectives, architecture) |
| **Project Setup** | `main.py` with lifespan hooks, startup/shutdown for outbox processor, CORS, router registration |
| **Documentation** | `README.md` sections on architecture, quick start, Docker setup |

**Marks covered:** Proposal & Report (10%), Database (schema design), Writing

**Demo slides to present:**
- Slide: Architecture diagram — "Why two databases?"
- Slide: Docker Compose — "One command starts everything"
- Slide: Tables overview — "8 PostgreSQL tables, 4 MongoDB collections"

---

### 2. Faris Zharfan — *Backend API & Complex SQL*

**Focus:** REST API Routes, JWT Authentication, Advanced SQL Queries

| Deliverable | Details |
|-------------|---------|
| **Auth API** | `api/auth.py` — JWT registration/login with bcrypt, role-based access (customer/admin), token validation |
| **Orders API** | `api/orders.py` — Full ACID order creation, stock validation, multi-item transactions |
| **Analytics API** | `api/analytics.py` — 9 endpoints: RFM, market basket, funnel, cart abandonment, alerts, audit, top products, sales by category, with admin-only protection |
| **Advanced SQL** | `services/relational_service.py` — RFM CTE with NTILE(4), market basket self-join, audit trail queries, top products aggregation |
| **Products API** | `api/products.py` — Paginated catalog with category filter, text search |

**Marks covered:** Database (40% — CRUD, advanced queries, security), Application (20% — API design)

**Demo slides to present:**
- Slide: API overview — "18 REST endpoints, Swagger docs"
- Slide: RFM Segmentation demo — "CTE + NTILE(4) = 5 customer segments"
- Slide: Market Basket Analysis — "Self-join finds products bought together"

---

### 3. Lucas Leow — *MongoDB & NoSQL Design*

**Focus:** MongoDB Schema, Bucket Pattern, Fraud Detection

| Deliverable | Details |
|-------------|---------|
| **NoSQL Schema** | `models/nosql_schemas.py` — Pydantic models for all 4 MongoDB collections |
| **Bucket Pattern** | `services/nosql_service.py` — Clickstream event recording with `$push` + `$inc`, upsert logic |
| **Funnel Analytics** | MongoDB `$facet` aggregation pipeline — 4-stage conversion funnel (page_view → add_to_cart → checkout → purchase) |
| **Cart Abandonment** | Aggregation detecting sessions with add_to_cart but no checkout |
| **Fraud Detection** | Cross-DB pipeline: MongoDB session velocity check → PostgreSQL alert insertion |
| **Cart API** | `api/cart.py` — Event recording endpoints with fraud check integration |
| **MongoDB Indexes** | Compound unique index, TTL index (30-day auto-delete), flagged index, timestamp index |

**Marks covered:** Database (40% — NoSQL design, advanced queries, patterns), Application (20% — fraud detection)

**Demo slides to present:**
- Slide: MongoDB collections — "4 collections, 4 design patterns"
- Slide: Bucket Pattern demo — "$push + $inc = O(1) event recording"
- Slide: Fraud Detection demo — "10 clicks in 60s = 🚨 FRAUD ALERT"

---

### 4. Muhammad Hasan Bin Suwandi — *CDC & Data Pipeline*

**Focus:** Cross-Database Sync, Data Loader, Integration Testing

| Deliverable | Details |
|-------------|---------|
| **CDC / Outbox Pattern** | `services/sync_service.py` — Async background poller (5s interval), processes outbox events, syncs to MongoDB `customer_order_summary` via `$inc` |
| **Data Loader** | `data_loader.py` — CSV ingestion pipeline for 6 datasets (~275k rows), creates Customer + User records, batch commits, UUID mapping |
| **Database Reset** | `reset_db.py` — Wipes both databases and recreates schema + triggers |
| **Integration Testing** | Verified CDC end-to-end: order creation → outbox event → MongoDB sync within 10 seconds |
| **Bug Fixes** | Identified and fixed hardcoded bcrypt hash issue, dead code cleanup in frontend components |

**Marks covered:** Database (40% — CDC, cross-DB integration), Application (20% — data pipeline)

**Demo slides to present:**
- Slide: CDC / Outbox Pattern — "PostgreSQL trigger → async poller → MongoDB sync"
- Slide: Data Pipeline — "6 CSVs → 275k rows → both databases"
- Slide: Integration test — "Order → wait 5s → MongoDB has the summary"

---

### 5. Muhammad Raees Irfan Bin Ishak — *Frontend & UX*

**Focus:** React Application, Admin Dashboard, Visual Design

| Deliverable | Details |
|-------------|---------|
| **React Frontend** | Complete SPA with React 18 + Vite: routing, state management, API client (`api.js`) |
| **Admin Dashboard** | `AdminDashboard.jsx` — RFM pie chart (Recharts), funnel bar chart, alerts table, top products, market basket, stat cards, tab navigation |
| **UX Design** | `index.css` — CSS design system with variables, gradient backgrounds, product cards with hover animations, toast notifications, responsive design, loading spinners |
| **Cart System** | Shopping cart with localStorage persistence, quantity controls, subtotals, checkout flow |
| **Product Catalog** | Category-based icons (⚡👗💄📚🏠⚽🎮), stock color coding, search/filter/pagination |
| **Login/Register** | Auth forms with validation, demo credentials card, role-based redirect |

**Marks covered:** Application (20% — frontend implementation, UX/UI), Presentation (15% — demo visuals)

**Demo slides to present:**
- Slide: Frontend tour — "4 pages: Catalog, Cart, Admin, Login"
- Slide: Admin Dashboard — "RFM pie chart, funnel bar, real-time alerts"
- Slide: UX features — "Toast notifications, cart badges, category icons"

---

### 6. Muhammad 'Afif Bin Muhd Lotfi Jarhom — *Triggers, Benchmarks & Final Report*

**Focus:** PostgreSQL Triggers, Performance Evaluation, Report Writing

| Deliverable | Details |
|-------------|---------|
| **PostgreSQL Triggers** | `triggers.sql` — 4 triggers: `trg_check_stock` (BEFORE INSERT), `trg_deduct_inventory` (AFTER INSERT), `trg_outbox_order` (AFTER INSERT), `trg_audit_order` (AFTER UPDATE) |
| **Benchmark Suite** | `benchmark/benchmark_runner.py` — 4 performance tests: MongoDB bulk insert (10k events), PostgreSQL hotspot contention (200 txns), 5-table JOIN, MongoDB aggregation pipeline. Results plotted via matplotlib |
| **Final Report** | `docs/G11_Final_Report.md` + DOCX generation — authored core sections: schema design, triggers, performance evaluation, constraints & limitations |
| **ER Diagram** | `docs/ER_Diagram.md` + auto-generated `ER_Diagram.png` (9600×5400 px, 300 DPI) — complete visual with all 8 tables + 4 collections, relationships, triggers, CDC flow |
| **Test Suite** | `tests/test_suite.py` — 161 automated tests covering all endpoints, triggers, and error cases |

**Marks covered:** Database (40% — triggers, performance), Writing (15% — final report), Presentation (15% — slides)

**Demo slides to present:**
- Slide: Triggers explained — "4 automatic rules: stock check, deduction, outbox, audit"
- Slide: Benchmark results — "MongoDB wins bulk insert, PostgreSQL wins JOINs"
- Slide: ER Diagram — "Complete database design in one picture"

---

## Collective Contributions (All Members)

| Activity | All Members Involved |
|----------|---------------------|
| **Code Review** | Every pull request reviewed by at least one other member |
| **Integration Testing** | All members tested their components end-to-end |
| **Documentation** | `walkthrough.md`, `demoguide.md`, `DOCKER_TROUBLESHOOTING.md` written collaboratively |
| **GenAI Reflection** | Section in Final Report — all members contributed their experiences |
| **Presentation Video** | All 6 members present their sections (see demo plan below) |

---

## Demo Presentation Plan (All Members Speak)

| Order | Member | Topic | Time |
|-------|--------|-------|------|
| 1 | **Hanzalah** | Architecture overview, Docker setup, database schema | 1.5 min |
| 2 | **Faris** | API design, RFM segmentation, market basket demo | 1.5 min |
| 3 | **Lucas** | MongoDB patterns, funnel analytics, fraud detection demo | 1.5 min |
| 4 | **Hasan** | CDC/Outbox sync, data pipeline, integration testing | 1.5 min |
| 5 | **Raees** | Frontend tour, admin dashboard, UX features | 1.5 min |
| 6 | **'Afif** | Triggers deep dive, benchmark results, report highlights | 1.5 min |
| — | **All** | Q&A, wrap-up | 1 min |

**Total: ~10 minutes** (target for video presentation)

---

## Mark Weightage Summary

| Component | % | Primary Owners |
|-----------|----|----------------|
| Proposal & Progress Report | 10% | Hanzalah (lead author), all contributed |
| Presentation (video) | 15% | All 6 members (1.5 min each) |
| **Database Design & Implementation** | **40%** | Faris (SQL), Lucas (NoSQL), 'Afif (triggers), Hasan (CDC), Hanzalah (schema) |
| **Application** | **20%** | Raees (frontend), Hasan (pipeline), Lucas (fraud), Faris (API) |
| **Writing (Final Report)** | **15%** | 'Afif (lead), all contributed sections |

---

*INF2003 Group 11 — Team Hanzalians — June 2026*
