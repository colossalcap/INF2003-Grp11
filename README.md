# 🛒 INF2003 Group 11 — E-Commerce Clickstream & Transaction Analytics

**Dual-database analytics platform: PostgreSQL (ACID transactions) + MongoDB (clickstream analytics)**

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     React Frontend (Vite)                         │
│              Port 3000 — Product Catalog, Cart, Admin             │
└─────────────────────────────┬────────────────────────────────────┘
                              │ REST API (JWT)
┌─────────────────────────────▼────────────────────────────────────┐
│                   FastAPI Backend (Python 3.11+)                   │
│                         Port 8000                                  │
│  ┌───────────┐  ┌──────────────┐  ┌────────────────────────────┐ │
│  │ Auth API  │  │ Order API    │  │ Analytics API               │ │
│  │ (JWT)     │  │ (ACID Txns)  │  │ (RFM, Funnel, Mkt Basket)  │ │
│  └───────────┘  └──────┬───────┘  └────────┬───────────────────┘ │
│  ┌───────────┐         │                    │                     │
│  │ Cart API  │         │                    │                     │
│  │ (MongoDB) │         │                    │                     │
│  └─────┬─────┘         │                    │                     │
└────────┼───────────────┼────────────────────┼─────────────────────┘
         │               │                    │
┌────────▼───────────────▼────────────────────▼─────────────────────┐
│                        Data Layer                                  │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐  │
│  │  PostgreSQL 15       │  │  MongoDB 7                       │  │
│  │  ─────────────────── │  │  ─────────────────────────────── │  │
│  │  • customers         │  │  • user_sessions (Bucket)        │  │
│  │  • products          │  │  • session_stats (Computed)      │  │
│  │  • orders            │  │  • customer_order_summary (CDC)  │  │
│  │  • order_items       │  │  • funnel_metrics (Cached)       │  │
│  │  • outbox (CDC)      │  │                                   │  │
│  │  • alerts            │  │                                   │  │
│  │  • order_audit_log   │  │                                   │  │
│  │  • users (auth)      │  │                                   │  │
│  └──────────────────────┘  └──────────────────────────────────┘  │
│  Triggers: Stock Check, Inventory Deduction, Outbox, Audit        │
└───────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites
- Docker Desktop (with Docker Compose)
- Python 3.11+ (for local development)

### One-Command Start

```bash
cd INF2003-Grp11
docker-compose up
```

This starts:
- **PostgreSQL** on port `5432` (with triggers auto-loaded)
- **MongoDB** on port `27017`
- **Backend API** on port `8000` (Swagger: http://localhost:8000/docs)
- **Frontend** on port `3000` (http://localhost:3000)

### Load Sample Data

```bash
# Connect to the backend container
docker exec -it ecommerce-backend bash

# Run the data loader
python data_loader.py
```

This loads the CSV files from `data/` into both databases:
- `customers.csv` → PostgreSQL `customers`
- `products.csv` → PostgreSQL `products`
- `orders.csv` + `order_items.csv` → PostgreSQL `orders` + `order_items`
- `events.csv` → MongoDB `user_sessions` (Bucket Pattern)

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register new user |
| `POST` | `/api/auth/login` | Login (returns JWT) |
| `GET` | `/api/auth/me` | Get current user |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/products/` | List products (pagination, category filter) |
| `GET` | `/api/products/{id}` | Get product details |
| `GET` | `/api/products/categories/all` | List all categories |

### Cart & Clickstream (MongoDB)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/cart/event` | Record clickstream event (Bucket Pattern) |
| `GET` | `/api/cart/session/{id}` | Get session events |

### Orders (PostgreSQL)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/orders/` | Create order (ACID transaction) |
| `GET` | `/api/orders/{id}` | Get order with items |
| `GET` | `/api/orders/` | List recent orders |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/analytics/rfm` | RFM segmentation (SQL CTEs + NTILE) |
| `GET` | `/api/analytics/market-basket` | Market basket analysis (self-join) |
| `GET` | `/api/analytics/funnel` | Funnel analytics (MongoDB $facet) |
| `GET` | `/api/analytics/cart-abandonment` | Cart abandonment detection |
| `GET` | `/api/analytics/alerts` | Fraud alerts (admin only) |
| `GET` | `/api/analytics/audit/{order_id}` | Order audit trail (admin only) |
| `GET` | `/api/analytics/top-products` | Top-selling products |
| `GET` | `/api/analytics/sales-by-category` | Sales by category |

---

## Advanced Features Location

| Feature | File | Line/Function |
|---------|------|---------------|
| **Stock Check Trigger** | `backend/triggers.sql` | `check_stock_before_order()` |
| **Inventory Deduction Trigger** | `backend/triggers.sql` | `deduct_inventory_after_order()` |
| **Outbox Trigger (CDC)** | `backend/triggers.sql` | `outbox_on_order_created()` |
| **Audit Trigger** | `backend/triggers.sql` | `audit_order_status_change()` |
| **RFM Segmentation** | `backend/services/relational_service.py` | `compute_rfm_segmentation()` |
| **Market Basket Analysis** | `backend/services/relational_service.py` | `compute_market_basket()` |
| **Session Funnel** | `backend/services/nosql_service.py` | `compute_funnel_metrics()` |
| **Fraud Detection** | `backend/services/nosql_service.py` | `check_fraud_alert()` |
| **Outbox Processor (CDC)** | `backend/services/sync_service.py` | `process_outbox_batch()` |
| **Bucket Pattern** | `backend/services/nosql_service.py` | `track_clickstream_event()` |
| **Computed Pattern** | `backend/services/nosql_service.py` | `compute_session_stats()` |
| **Data Loader** | `backend/data_loader.py` | `run_data_loader()` |
| **Benchmark Suite** | `backend/benchmark/benchmark_runner.py` | `run_all_benchmarks()` |

---

## Database Design

### PostgreSQL — Relational (ACID)

| Table | Purpose | Key Features |
|-------|---------|-------------|
| `customers` | Customer profiles | UUID PK, country_code |
| `products` | Product catalog | CHECK stock_quantity >= 0 |
| `orders` | Order headers | FK to customers, status tracking |
| `order_items` | Line items | FK to orders + products, triggers fire |
| `outbox` | CDC event store | JSONB payload, processed flag |
| `alerts` | Fraud alerts | Linked to customers |
| `order_audit_log` | Change history | Populated by audit trigger |
| `users` | Auth accounts | Hashed passwords, JWT tokens |

### MongoDB — NoSQL (BASE)

| Collection | Pattern | Purpose |
|------------|---------|---------|
| `user_sessions` | **Bucket** | Accumulates clickstream events, updates via `$push` + `$inc` |
| `session_stats` | **Computed** | Pre-aggregated session summary |
| `customer_order_summary` | **CDC Target** | Denormalized view synced from PostgreSQL via Outbox |
| `funnel_metrics` | **Cached** | Aggregated conversion funnel results |

---

## Benchmarking

Run the benchmark suite:

```bash
docker exec -it ecommerce-backend python benchmark/benchmark_runner.py
```

This measures:
1. **MongoDB Bulk Insert** — 10k clickstream events via Bucket Pattern
2. **PostgreSQL Hotspot** — Concurrent UPDATEs under contention (200 txns)
3. **PostgreSQL 5-Table JOIN** — Orders + Customers + Items + Products
4. **MongoDB Aggregation** — $unwind + $group equivalent

Results are plotted to `backend/benchmark/plots/benchmark_results.png`.

---

## Project Structure

```
INF2003-Grp11/
├── docker-compose.yml          # One-command startup
├── .env.example                # Environment variable template
├── README.md
├── data/                       # CSV datasets
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   ├── order_items.csv
│   ├── clickstream_events.csv
│   └── sessions.csv
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Environment-based config
│   ├── triggers.sql            # PostgreSQL triggers
│   ├── data_loader.py          # CSV → DB loader
│   ├── models/
│   │   ├── relational.py       # SQLAlchemy ORM models
│   │   └── nosql_schemas.py    # Pydantic MongoDB models
│   ├── api/
│   │   ├── auth.py             # JWT auth endpoints
│   │   ├── products.py         # Product catalog
│   │   ├── cart.py             # Clickstream + fraud detection
│   │   ├── orders.py           # Order creation (transactions)
│   │   └── analytics.py        # RFM, funnel, basket, audit
│   ├── services/
│   │   ├── relational_service.py  # Complex SQL queries
│   │   ├── nosql_service.py       # MongoDB operations
│   │   └── sync_service.py        # Outbox/CDC processor
│   └── benchmark/
│       ├── benchmark_runner.py    # Performance test suite
│       └── plots/                 # Generated charts
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx
        ├── api.js                # Backend API client
        ├── index.css
        └── components/
            ├── Login.jsx
            ├── ProductList.jsx
            ├── Cart.jsx
            └── AdminDashboard.jsx
```

---

## Group 11 — INF2003

| Deliverable | Deadline |
|-------------|----------|
| Progress Report | Mon, Jun 22, 2026 |
| Slides, Video, Final Report, Source Code | Mon, Jul 13, 2026 |
| Peer Review | Fri, Jul 17, 2026 |
