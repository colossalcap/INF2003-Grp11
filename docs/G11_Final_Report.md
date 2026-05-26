# G11 — Final Report (Template)
## INF2003 Group Project — E-Commerce Clickstream & Transaction Analytics

> Max 8 pages (excluding cover page and appendix). Submit as `G11_Final Report.PDF`.

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
| **Submission Date** | July 13, 2026 |

---

## 1. Introduction

This project demonstrates a dual-database e-commerce analytics platform: PostgreSQL handles ACID transactions (orders, inventory), while MongoDB handles BASE clickstream analytics (user sessions, funnel conversion). The Outbox Pattern provides CDC synchronization between the two systems.

---

## 2. System-Level Database Integration

### 2.1 Architecture
FastAPI connects to PostgreSQL via SQLAlchemy (ORM + raw SQL) and to MongoDB via Motor (async driver). The Outbox Pattern bridges the two: after each order commit, a PostgreSQL trigger writes to the `outbox` table, and a background async poller syncs denormalized summaries to MongoDB's `customer_order_summary` collection.

### 2.2 Consistency Strategy
- **Write Path**: PostgreSQL-first (ACID) → Outbox trigger → Async poller → MongoDB (eventual consistency)
- **Read Path**: Queries target the appropriate database directly (no cross-DB JOINs)
- **Failure Handling**: Unprocessed outbox events are retried on the next poll cycle

---

## 3. Relational Database (PostgreSQL)

### 3.1 Schema (7 Tables)
`users`, `customers`, `products`, `orders`, `order_items`, `outbox`, `order_audit_log`, `alerts`

### 3.2 Triggers (4)
`trg_check_stock`, `trg_deduct_inventory`, `trg_outbox_order`, `trg_audit_order`

### 3.3 Advanced SQL
- **RFM**: CTE + NTILE(4) → Champions/Loyal/At Risk/Lost
- **Market Basket**: Self-join on order_items for co-occurrence
- **Audit Trail**: Full change history from trigger-populated log

---

## 4. NoSQL Database (MongoDB)

### 4.1 Collections (4)
`user_sessions` (Bucket), `session_stats` (Computed), `customer_order_summary` (CDC), `funnel_metrics` (Cached)

### 4.2 Advanced Queries
- **$facet Funnel**: page_view → add_to_cart → checkout → purchase conversion rates
- **Cart Abandonment**: Aggregation detecting sessions with add_to_cart but no checkout
- **TTL Index**: Auto-delete sessions after 30 days

---

## 5. Application Implementation

### 5.1 Web Interface (React + Recharts)
[Insert up to 10 screenshots of Login, Product Catalog, Cart, Admin Dashboard with charts]

### 5.2 Key Features
- JWT authentication with bcrypt
- Product catalog with category filter, search, pagination
- Clickstream event tracking (Bucket Pattern)
- Order creation with full ACID transaction + triggers
- Real-time fraud detection (rapid cart activity → alerts)
- Admin dashboard with RFM pie chart, funnel bar chart, alerts table, top products

---

## 6. Performance Evaluation

[Insert `benchmark_results.png` from `backend/benchmark/plots/`]

| Test | Database | Measurement |
|------|----------|-------------|
| Bulk Insert (10k events) | MongoDB | ops/sec |
| Hotspot UPDATEs (200 txns) | PostgreSQL | txns/sec |
| 5-Table JOIN | PostgreSQL | ms |
| Aggregation Pipeline | MongoDB | ms |

---

## 7. Constraints & Limitations

- Outbox polling introduces ~5s staleness for CDC data
- Fraud detection uses simple threshold counting (production would use ML)
- No distributed tracing or production observability

---

## 8. Discussion & Reflections

### 8.1 What Worked Well
- Clear separation: PostgreSQL for transactions, MongoDB for analytics
- Outbox Pattern provided reliable CDC without Kafka/Debezium
- Triggers simplified inventory management — no app-level stock logic
- MongoDB Bucket Pattern perfectly matched clickstream use case

### 8.2 Challenges
- Cross-database consistency requires application-level coordination
- Debugging trigger failures requires PostgreSQL server log access

### 8.3 Future Improvements
- Add Kafka + Debezium for real-time CDC
- Redis caching for product catalog
- Cloud deployment (AWS RDS + MongoDB Atlas)

---

## Appendix (not counted in page limit)

- SQL triggers: `backend/triggers.sql`
- MongoDB operations: `backend/services/nosql_service.py`
- SQL queries: `backend/services/relational_service.py`
- Benchmark: `backend/benchmark/benchmark_runner.py`
- Docker: `docker-compose.yml`

---

*End of Final Report*
