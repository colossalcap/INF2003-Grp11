# G11 — Progress Report (Template)
## INF2003 Group Project — E-Commerce Clickstream & Transaction Analytics

> Max 4 pages (excluding cover page). Submit as `G11_Progress Report.pdf`.

---

## Cover Page

| Field | Detail |
|-------|--------|
| **Module** | INF2003 Database Design & Implementation |
| **Group ID** | G11 |
| **Project Title** | E-Commerce Clickstream & Transaction Analytics |
| **Topic** | Topic 2 — Dual-Database Analytics Platform |
| **Team Members** | [Name 1], [Name 2], [Name 3], [Name 4] |
| **Team Lead** | [Name] ([email]) |
| **Submission Date** | June 22, 2026 |

---

## 1. Application Background & Problem Statement

### 1.1 Background
Modern e-commerce platforms generate two fundamentally different types of data: transactional data (orders, payments, inventory) requiring strict ACID guarantees, and behavioral/clickstream data (page views, cart actions) that is high-volume and schema-flexible. A dual-database architecture addresses both needs simultaneously.

### 1.2 Objectives
1. Design a normalized PostgreSQL schema (7 tables) with ACID transactions
2. Implement MongoDB collections using Bucket, Computed, and CDC patterns
3. Deploy 4 PostgreSQL triggers (stock check, inventory deduction, outbox, audit)
4. Implement CDC via Outbox Pattern (PostgreSQL → MongoDB)
5. Build complex SQL: RFM segmentation (CTEs + NTILE), market basket (self-join)
6. Build MongoDB aggregations: $facet funnel, cart abandonment detection
7. Real-time fraud detection (MongoDB session analysis → PostgreSQL alerts)
8. React web dashboard with Recharts visualizations

---

## 2. System Architecture

```
React (Vite) ──REST/JWT──> FastAPI ──SQLAlchemy──> PostgreSQL
                   │                          ├── 4 Triggers
                   │                          ├── Outbox Table
                   │                          └── CDC ──> MongoDB
                   │
                   └──Motor (async)──> MongoDB
                                      ├── user_sessions (Bucket)
                                      ├── session_stats (Computed)
                                      ├── customer_order_summary (CDC)
                                      └── funnel_metrics (Cached)
```

---

## 3. Dataset Description

| Source | File | Records | Purpose |
|--------|------|---------|---------|
| E-Commerce Dataset | `customers.csv` | ~13,000 | Customer profiles |
| E-Commerce Dataset | `products.csv` | ~1,000 | Product catalog |
| E-Commerce Dataset | `orders.csv` | ~10,000 | Order transactions |
| E-Commerce Dataset | `order_items.csv` | ~25,000 | Line items per order |
| E-Commerce Dataset | `events.csv` | ~100,000 | Clickstream events |
| E-Commerce Dataset | `sessions.csv` | ~10,000 | Session metadata |

---

## 4. Planned Functionalities

| Feature | Database | Technique |
|---------|----------|-----------|
| User Auth (JWT) | PostgreSQL `users` | bcrypt + python-jose |
| Product Catalog | PostgreSQL `products` | Paginated REST API |
| Clickstream Tracking | MongoDB `user_sessions` | Bucket Pattern ($push + $inc) |
| Order Creation | PostgreSQL | ACID transaction + 4 triggers |
| Fraud Detection | MongoDB → PostgreSQL | Session analysis → alerts table |
| CDC Sync | PostgreSQL → MongoDB | Outbox Pattern (async poller) |
| RFM Segmentation | PostgreSQL | CTE + NTILE(4) window function |
| Market Basket | PostgreSQL | Self-join on order_items |
| Funnel Analytics | MongoDB | $facet aggregation pipeline |
| Admin Dashboard | React + Recharts | Pie, bar charts, tables |

---

## 5. Implementation Progress (as of Jun 22)

| Component | Status |
|-----------|--------|
| PostgreSQL Schema (7 tables) | ✅ Complete |
| ER Diagram | ✅ Complete |
| 4 PostgreSQL Triggers | ✅ Complete |
| MongoDB Schema (4 collections) | ✅ Complete |
| Backend API (6 route modules) | ✅ Complete |
| Data Loader (CSV → DB) | ✅ Complete |
| CDC/Outbox Processor | ✅ Complete |
| Benchmark Suite (4 tests) | ✅ Complete |
| React Frontend (4 components) | ✅ Complete |
| Docker Compose | ✅ Complete |

---

## 6. Timeline

```
Week 1-2 (May 26 - Jun 8):   Schema design, ERD, dataset preparation
Week 3-4 (Jun 9 - Jun 22):   Backend + Frontend, Progress Report
Week 5-6 (Jun 23 - Jul 6):   Integration testing, bug fixes
Week 7   (Jul 7 - Jul 13):   Final report, slides, video
Week 8   (Jul 14 - Jul 17):  Peer review
```

---

*End of Progress Report*
