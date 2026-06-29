# 🛒 INF2003 Group 11 — E-Commerce Clickstream & Transaction Analytics

<div align="center">

**Dual-Database Analytics Platform — PostgreSQL (ACID) + MongoDB (BASE)**

[![Tests](https://img.shields.io/badge/tests-161%2F161%20passed-brightgreen)](#-test-suite)
[![Docker](https://img.shields.io/badge/docker-4%20containers-blue)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3.11+-yellow)](https://www.python.org/)
[![React](https://img.shields.io/badge/react-18+-61dafb)](https://react.dev/)
[![INF2003](https://img.shields.io/badge/module-INF2003%20SIT-red)]()

**Group 11 — Team Hanzalians** · Singapore Institute of Technology · June 2026

</div>

---

## 📖 Documentation Map

| Document | Audience | Purpose |
|----------|----------|---------|
| **`README.md`** (this file) | Developers & Evaluators | Technical overview, API reference, architecture |
| **`walkthrough.md`** | Everyone (no coding knowledge needed) | Friendly guide with glossary, analogies, step-by-step instructions |
| **`demoguide.md`** | Team members doing demos | Scripted walkthrough of every feature for presentations & video |
| **`DOCKER_TROUBLESHOOTING.md`** | Anyone debugging setup issues | 12+ common Docker problems with diagnostic commands and fixes |
| **`docs/ER_Diagram.md`** | Database Designers | Full entity-relationship diagram with relationships |
| **`docs/G11_Final_Report.md`** | Academic Submission | 8-page final report covering all INF2003 requirements |
| **`docs/G11_Progress_Report.md`** | Academic Submission | Mid-project progress report |

> **New to this project?** Start with [`walkthrough.md`](walkthrough.md). **Doing a demo?** Use [`demoguide.md`](demoguide.md). **Docker issues?** See [`DOCKER_TROUBLESHOOTING.md`](DOCKER_TROUBLESHOOTING.md).
> **Having Docker problems?** See [`DOCKER_TROUBLESHOOTING.md`](DOCKER_TROUBLESHOOTING.md) — 12 common issues with step-by-step fixes.

---

## 🚀 Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (includes Docker Compose)
- **Troubleshooting:** If you run into issues, check [`DOCKER_TROUBLESHOOTING.md`](DOCKER_TROUBLESHOOTING.md) first — it covers port conflicts, WSL2 setup, memory limits, permission issues, and more.

### One Command

```bash
cd INF2003-Grp11
docker-compose up
```

This starts all 4 containers:

| Container | Technology | Port | Purpose |
|-----------|-----------|------|---------|
| `ecommerce-postgres` | PostgreSQL 15 | `5432` | ACID transactions — orders, inventory, customers |
| `ecommerce-mongodb` | MongoDB 7 | `27017` | BASE analytics — clickstream, sessions, funnel |
| `ecommerce-backend` | FastAPI (Python 3.11) | `8000` | REST API + Swagger docs |
| `ecommerce-frontend` | React (Vite) | `3000` | Product catalog, cart, admin dashboard |
| `ecommerce-data-loader` | Python (one-shot) | — | Auto-loads CSV data into both databases, then exits |

> **The data loader runs automatically on first start!** By default it runs in **demo mode** (~1.5 min) loading 2K customers, 1.2K products, 3K orders, and 40K clickstream events — enough to demonstrate ALL features. To load the full 275K-row dataset, set `DEMO_MODE = False` in `backend/data_loader.py`, then reset and rebuild:
> ```bash
> docker compose --profile reset up reset-db && docker compose build data-loader && docker compose up -d data-loader
> ```
> To skip the data loader on subsequent runs, comment out the `data-loader` section in `docker-compose.yml`.

### Dataset Sources

| Dataset | Kaggle Link | Records Used |
|---------|------------|-------------|
| E-commerce Clickstream and Transaction Dataset | [waqi786](https://www.kaggle.com/datasets/waqi786/e-commerce-clickstream-and-transaction-dataset) | ~200,000 events |
| Synthetic E-commerce Transactions + Clickstream 2020–2025 | [wafaaelhusseini](https://www.kaggle.com/datasets/wafaaelhusseini/e-commerce-transactions-clickstream) | ~75,000 transactions |

Combined into 6 CSV files in `data/`: `customers.csv`, `products.csv`, `orders.csv`, `order_items.csv`, `clickstream_events.csv`, `sessions.csv` — totaling ~275,000 rows.

### ⚡ Data Loader Performance

| Mode | Customers | Products | Orders | Clickstream Events | Sessions | Load Time |
|------|-----------|----------|--------|--------------------|----------|-----------|
| **Demo** (default) | 2,000 | 1,197 | 3,000 | 40,000 | 10,000 | **~1.5 min** |
| **Full** | 20,000 | 1,197 | 33,580 | 760,958 | 120,000 | ~20 min |

**How we achieved the 13× speedup:**
1. **Batch MongoDB writes** — Instead of 761K individual `update_one` calls, events are grouped by session in memory and pushed with a single `$push: { $each: [...] }` per session
2. **Sampling with `nrows`** — CSV files are read with `pd.read_csv(nrows=N)` instead of loading all rows then filtering
3. **Bulk session inserts** — 10K sessions inserted via `insert_many(ordered=False)` instead of individual upserts
4. **Shared bcrypt hash** — Password hash computed once outside the loop (saves ~83 minutes on full dataset)

Toggle demo/full mode by editing `DEMO_MODE` at the top of `backend/data_loader.py`.

### Load Sample Data (Manual — only if you skipped the auto-loader)

```bash
docker exec -it ecommerce-backend python data_loader.py
```

### Access the Application

| URL | What |
|-----|------|
| http://localhost:3000 | **Frontend** — browse products, manage cart, view analytics |
| http://localhost:8000/docs | **Swagger UI** — interactive API documentation |
| http://localhost:8000/ | **API root** — health check |

### � Default Credentials

| Role | Username | Password | How to get |
|------|----------|----------|------------|
| **Admin** | Register any account, then promote: `docker exec ecommerce-backend python promote_admin.py <username>` | — | Or use a pre-promoted account from test suite |
| **Customer** | Register at `/login` | — | Create your own account |
| **Legacy** | `user_1` | `password123` | From data loader (customer role only) |

> ⚠️ Legacy accounts from the data loader have **customer** role by default. To access the **Admin Dashboard**, register a new account and promote it to admin using the command above.

### �🔄 Reset Databases (Fresh Start)

Wipe all data and start clean — useful for demos or troubleshooting:

```bash
# 1. Stop everything
docker-compose down

# 2. Wipe both databases
docker-compose --profile reset up reset-db

# 3. Start fresh (auto-loads data)
docker-compose up
```

Or as a one-liner:
```bash
docker-compose down && docker-compose --profile reset up reset-db && docker-compose up
```

---

## 🏗️ Architecture

```
                    ┌──────────────────────────┐
                    │   React Frontend (Vite)   │
                    │        Port 3000           │
                    │  Catalog │ Cart │ Admin    │
                    └────────────┬───────────────┘
                                 │ REST (JWT Auth)
                    ┌────────────▼───────────────┐
                    │   FastAPI Backend (Python)  │
                    │        Port 8000            │
                    │                             │
                    │  POST /api/auth/*     Auth  │
                    │  GET  /api/products/*  Cat  │
                    │  POST /api/cart/*     Cart  │
                    │  POST /api/orders/*   Order │
                    │  GET  /api/analytics/* Stats│
                    └──────┬──────────┬───────────┘
                           │          │
              SQLAlchemy   │          │  Motor (async)
              (ORM)        │          │
                    ┌──────▼────┐ ┌──▼───────────┐
                    │ PostgreSQL│ │   MongoDB     │
                    │  :5432    │ │   :27017      │
                    │           │ │               │
                    │ 8 Tables  │ │ 4 Collections │
                    │ 4 Triggers│ │ 4 Patterns    │
                    │ ACID      │ │ BASE          │
                    └──────┬────┘ └───────────────┘
                           │
                   Outbox  │ CDC (async poller)
                   Pattern │
                           ▼
                    ┌──────────────────────────────┐
                    │  customer_order_summary       │
                    │  (MongoDB — denormalized view) │
                    └──────────────────────────────┘
```

**Data Routing:**
- **Browsing data** (page views, cart actions) → MongoDB — Bucket Pattern, near O(1) insert
- **Purchase data** (orders, payments) → PostgreSQL — full ACID with trigger cascade
- **CDC Bridge** — Outbox Pattern: PostgreSQL trigger → async poller → MongoDB sync
- **Fraud Detection** — MongoDB session velocity check → PostgreSQL alerts insertion

---

## 📊 Database Design

### PostgreSQL — Relational (8 Tables, ACID)

| Table | Row Count | Key Features |
|-------|-----------|-------------|
| `users` | ~2,000 (demo) / 20,000 (full) | JWT auth, bcrypt passwords, admin/customer roles |
| `customers` | ~2,000 (demo) / 20,000 (full) | UUID PK, country_code, opt-in status |
| `products` | 1,197 | 7 categories, CHECK(stock_quantity >= 0), indexed by category |
| `orders` | ~3,000 (demo) / 33,580 (full) | FK → customers, status tracking, total_amount |
| `order_items` | varies with orders | FK → orders + products, triggers fire here |
| `outbox` | dynamic | CDC event store, JSONB payload, processed flag |
| `order_audit_log` | dynamic | Full change history (trigger-populated) |
| `alerts` | dynamic | Fraud detection results, acknowledged flag |

**Relationships:** customers 1:M orders, orders 1:M order_items, products 1:M order_items

### MongoDB — NoSQL (4 Collections, BASE)

| Collection | Pattern | Document Count | Purpose |
|------------|---------|---------------|---------|
| `user_sessions` | **Bucket** | ~10,000 (demo) / 120,000 (full) | Accumulates clickstream events via batch `$push` + `$each` |
| `session_stats` | **Computed** | ~10,000 (demo) / 120,000 (full) | Pre-aggregated session summaries |
| `customer_order_summary` | **CDC Target** | sync'd | Denormalized view from PostgreSQL via Outbox |
| `funnel_metrics` | **Cached** | on-demand | Aggregated conversion funnel results |

**Indexes:** Compound (customer_id, session_id), TTL (end_time, 30-day expiry), flagged, events.timestamp

---

## ⚡ PostgreSQL Triggers (4)

| # | Trigger | Event | Function |
|---|---------|-------|----------|
| 1 | `trg_check_stock` | BEFORE INSERT on order_items | Raises exception if stock insufficient |
| 2 | `trg_deduct_inventory` | AFTER INSERT on order_items | Decrements product stock_quantity |
| 3 | `trg_outbox_order` | AFTER INSERT on orders | Writes JSON event to outbox for CDC |
| 4 | `trg_audit_order` | AFTER UPDATE on orders | Logs old/new values to order_audit_log |

All triggers auto-deploy via `triggers.sql` mounted to `/docker-entrypoint-initdb.d/`.

---

## 📡 API Reference

### Authentication (JWT)

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/register` | None | Register new user → returns JWT |
| `POST` | `/api/auth/login` | None | OAuth2 login → returns JWT |
| `GET` | `/api/auth/me` | Bearer | Get current user profile |

**Request examples:**
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@test.com","password":"secret123","display_name":"John"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -d "grant_type=password&username=john&password=secret123"
```

### Products (Public)

| Method | Endpoint | Params | Description |
|--------|----------|--------|-------------|
| `GET` | `/api/products/` | `page`, `limit`, `category`, `search` | Paginated product list |
| `GET` | `/api/products/{id}` | — | Single product detail |
| `GET` | `/api/products/categories/all` | — | Distinct categories (7) |

### Cart & Clickstream (Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/cart/event` | Record clickstream event (Bucket Pattern) |
| `GET` | `/api/cart/session/{id}` | Get all events for a session |

**Event types:** `page_view`, `add_to_cart`, `checkout`, `purchase`

### Orders (Auth Required, ACID)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/orders/` | Create order (triggers cascade: stock check → deduction → outbox) |
| `GET` | `/api/orders/{id}` | Get order with line items |
| `GET` | `/api/orders/` | List recent orders (paginated) |

### Analytics (Auth Required)

| Method | Endpoint | DB | Technique |
|--------|----------|----|-----------|
| `GET` | `/api/analytics/rfm` | PostgreSQL | CTE + NTILE(4) → Champions/Loyal/At Risk/Lost |
| `GET` | `/api/analytics/market-basket?top_n=10` | PostgreSQL | Self-join on order_items |
| `GET` | `/api/analytics/funnel` | MongoDB | `$facet` aggregation pipeline |
| `GET` | `/api/analytics/cart-abandonment` | MongoDB | Aggregation: add_to_cart without checkout |
| `GET` | `/api/analytics/top-products?limit=10` | PostgreSQL | GROUP BY + ORDER BY total_sold |
| `GET` | `/api/analytics/sales-by-category` | PostgreSQL | GROUP BY category |
| `GET` | `/api/analytics/alerts` 🔒 | Both | Fraud alerts (admin only) |
| `GET` | `/api/analytics/audit/{order_id}` 🔒 | PostgreSQL | Order change history (admin only) |

🔒 = Admin role required

---

## 🧪 Test Suite

**161 automated tests** covering every feature. All passing as of last run.

```bash
docker exec -it ecommerce-backend python tests/test_suite.py
```

| Section | Tests | Coverage |
|---------|-------|----------|
| Health Checks | 7 | Root, health, Swagger, OpenAPI schema |
| Authentication | 12 | Register, login, /me, duplicates, bad passwords, invalid tokens |
| Products | 30 | List, pagination, category filter, search, get by ID, 404, categories |
| Cart/Clickstream | 16 | All 4 event types, invalid inputs, session retrieval, auto-ID |
| Orders (ACID) | 18 | Create, get, list, stock rejection, inventory deduction trigger, outbox |
| Analytics | 24 | RFM, market basket, funnel, cart abandonment, top products, sales |
| Admin Analytics | 7 | Alerts (admin/non-admin), audit trail (admin/non-admin/unauth) |
| Trigger Verification | 10 | All 4 functions + table attachments + CHECK constraint |
| MongoDB Verification | 10 | 4 collections, compound index, TTL, flagged, timestamp indexes |
| Error Handling | 6 | Empty body, short username, invalid email, short password, 404, bad pagination |

Example output:
```
  ✅ Passed:  161/161
  ❌ Failed:  0/161
  ⏱️  Time:    7.08s
  🎉 ALL TESTS PASSED!
```

---

## ⚡ Benchmark Suite

Performance comparison between PostgreSQL and MongoDB:

```bash
docker exec -it ecommerce-backend python benchmark/benchmark_runner.py
```

| Benchmark | DB | Operation | Metric |
|-----------|----|-----------|--------|
| Bulk Insert | MongoDB | 10k clickstream events (Bucket Pattern) | ops/sec |
| Hotspot Contention | PostgreSQL | 200 concurrent UPDATEs | latency |
| 5-Table JOIN | PostgreSQL | Orders + Customers + Items + Products | query time |
| Aggregation Pipeline | MongoDB | $unwind + $group equivalent | query time |

Results plotted to `backend/benchmark/plots/benchmark_results.png`.

---

## 🔑 Key Features Summary

| # | Feature | Implementation | INF2003 Req |
|---|---------|---------------|-------------|
| 1 | **Dual-database architecture** | PostgreSQL (ACID) + MongoDB (BASE) | Req 1, 3 |
| 2 | **≥3 tables, multiple relationships** | 8 tables, 1:M relationships | Req 3 |
| 3 | **ER Diagram** | `docs/ER_Diagram.md` | Req 3 |
| 4 | **CRUD on both DBs** | Products, orders, events, sessions | Req 4 |
| 5 | **Nested queries** | RFM CTEs, market basket self-join | Req 5 |
| 6 | **4 database triggers** | Stock, inventory, outbox, audit | Req 5 |
| 7 | **CDC / Outbox Pattern** | PostgreSQL → async poller → MongoDB | Req 5 |
| 8 | **NoSQL design patterns** | Bucket, Computed, CDC Target, Cached | Req 3 |
| 9 | **GenAI integration** | Documented in Final Report | Req 6 |
| 10 | **Performance analysis** | Benchmark suite with plots | Req 7 (opt) |
| 11 | **Web application** | React + Vite + Recharts + JWT | Req 8 (opt) |
| 12 | **Fraud detection** | MongoDB velocity check → PostgreSQL alert | Bonus |
| 13 | **Test suite** | 161 automated tests | Bonus |
| 14 | **Comprehensive docs** | README + walkthrough + ER diagram + reports | Bonus |

---

## 📁 Project Structure

```
INF2003-Grp11/
├── docker-compose.yml              ← One-command full-stack startup
├── README.md                       ← This file — technical overview
├── walkthrough.md                  ← Friendly guide for non-programmers
│
├── data/                           ← CSV datasets (~275k rows total)
│   ├── customers.csv               (20k rows)
│   ├── products.csv                (1.2k rows)
│   ├── orders.csv                  (53k rows)
│   ├── order_items.csv             (75k rows)
│   ├── clickstream_events.csv      (120k rows)
│   └── sessions.csv                (27.5k rows)
│
├── backend/                        ← FastAPI application
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                     ← Entry point + lifespan hooks
│   ├── config.py                   ← Env-based configuration
│   ├── triggers.sql                ← 4 PostgreSQL triggers (auto-deployed)
│   ├── data_loader.py              ← CSV → PostgreSQL + MongoDB
│   ├── api/                        ← Route handlers
│   │   ├── __init__.py
│   │   ├── auth.py                 ← JWT registration, login, /me
│   │   ├── products.py             ← Catalog listing, search, categories
│   │   ├── cart.py                 ← Clickstream events + fraud detection
│   │   ├── orders.py               ← Order creation (ACID transaction)
│   │   └── analytics.py            ← RFM, funnel, basket, alerts, audit
│   ├── models/                     ← Data structure definitions
│   │   ├── __init__.py
│   │   ├── relational.py           ← SQLAlchemy ORM (8 table classes)
│   │   └── nosql_schemas.py        ← Pydantic models (MongoDB documents)
│   ├── services/                   ← Business logic layer
│   │   ├── __init__.py
│   │   ├── relational_service.py   ← Complex SQL: RFM, market basket, alerts
│   │   ├── nosql_service.py        ← MongoDB: bucket, funnel, fraud, indexes
│   │   └── sync_service.py         ← Outbox CDC background processor
│   ├── tests/                      ← Testing
│   │   ├── __init__.py
│   │   └── test_suite.py           ← 161-test comprehensive suite
│   └── benchmark/                  ← Performance
│       ├── benchmark_runner.py     ← Speed/memory comparison
│       └── plots/                  ← Generated charts
│
├── frontend/                       ← React (Vite) SPA
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx                ← Entry point
│       ├── App.jsx                 ← Router + nav + auth state
│       ├── api.js                  ← Axios HTTP client (all endpoints)
│       ├── index.css               ← Global styles
│       └── components/
│           ├── Login.jsx           ← Login/register forms
│           ├── ProductList.jsx     ← Catalog with search/filter/pagination
│           ├── Cart.jsx            ← Shopping cart + clickstream tracking
│           └── AdminDashboard.jsx  ← Charts: RFM pie, funnel bar, alerts
│
└── docs/                           ← Documentation & reports
    ├── ER_Diagram.md               ← Entity-relationship diagram
    ├── G11_Final_Report.md         ← Final submission (8 pages)
    ├── G11_Progress_Report.md      ← Mid-project progress report
    └── G11_Progress_Report.docx    ← Progress report (Word format)
```

---

## 🔧 Configuration

All settings are in environment variables (defined in `docker-compose.yml` for Docker, or `.env` for local dev):

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `postgresql://ecommerce_user:ecommerce_pass@postgres:5432/ecommerce_db` | PostgreSQL connection |
| `MONGO_URI` | `mongodb://mongodb:27017` | MongoDB connection |
| `MONGO_DB` | `ecommerce_nosql` | MongoDB database name |
| `JWT_SECRET_KEY` | `change-this-to-a-random-secret-key` | JWT signing key (**change for production!**) |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `JWT_EXPIRE_MINUTES` | `60` | Token expiry time |
| `FRAUD_EVENT_THRESHOLD` | `10` | Events before fraud flag |
| `FRAUD_TIME_WINDOW_SECONDS` | `60` | Fraud detection time window |
| `OUTBOX_POLL_INTERVAL` | `5` | CDC poll interval (seconds) |
| `DEBUG` | `false` | SQLAlchemy query logging |

---

## 👥 Team

**Group 11 — Team Hanzalians** · INF2003 Database Design & Implementation · SIT

| Member | Role |
|--------|------|
| Hanzalah Hisam | **Team Lead** |
| Faris Zharfan | Member |
| Lucas Leow | Member |
| Muhammad Hasan Bin Suwandi | Member |
| Muhammad Raees Irfan Bin Ishak | Member |
| Muhammad 'Afif Bin Muhd Lotfi Jarhom | Member |

---

## 📋 Deliverables

| Deliverable | Deadline | Status |
|-------------|----------|--------|
| Progress Report | Mon, Jun 22, 2026 | ✅ Submitted |
| Final Report | Sun, Jul 13, 2026 | 📝 In progress |
| Source Code | Sun, Jul 13, 2026 | ✅ Complete |
| Presentation | TBD | 📝 In progress |

---

## 🛠️ Troubleshooting

### Common Issues (Quick Fix)

| Problem | Solution |
|---------|----------|
| "Port already allocated" | Stop other services using ports 5432/27017/8000/3000 |
| No products on website | Wait for `ecommerce-data-loader` to finish, then refresh |
| Login not working | Register a new account first at `/login` |
| "Admin access required" | Your account has `customer` role — need `admin` role |
| Tests fail | Ensure `docker-compose up` is running |
| Containers won't start | Run `docker-compose down -v` then `docker-compose up` |

### Docker-Specific Problems?

See the full guide: **[DOCKER_TROUBLESHOOTING.md](DOCKER_TROUBLESHOOTING.md)** — covers 12+ Docker issues including:

- Docker not installed / not running
- WSL2 setup (Windows)
- Port conflicts with diagnostics
- Memory/CPU limits
- Permission issues (Linux/Mac)
- Build cache problems
- Volume mount issues
- Docker Hub rate limiting
- Complete nuke-and-rebuild instructions

---

*INF2003 Group 11 — Singapore Institute of Technology — June 2026*
