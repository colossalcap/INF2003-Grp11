# 🎬 Demo Guide — INF2003 Group 11

**A step-by-step walkthrough for demonstrating every feature of the E-Commerce Clickstream & Transaction Analytics platform.**

---

## Table of Contents

1. [Quick Setup](#1-quick-setup)
2. [Demo 1: Product Browser (No Login)](#2-demo-1-product-browser-no-login)
3. [Demo 2: User Registration & Login](#3-demo-2-user-registration--login)
4. [Demo 3: Add to Cart & Clickstream Events](#4-demo-3-add-to-cart--clickstream-events)
5. [Demo 4: Place an Order (ACID Transaction + Triggers)](#5-demo-4-place-an-order-acid-transaction--triggers)
6. [Demo 5: Cart & Clickstream Page](#6-demo-5-cart--clickstream-page)
7. [Demo 6: Fraud Detection](#7-demo-6-fraud-detection)
8. [Demo 7: Admin Dashboard — All Analytics](#8-demo-7-admin-dashboard--all-analytics)
9. [Demo 8: Database Reset (Optional)](#9-demo-8-database-reset-optional)
10. [Quick Reference Card](#10-quick-reference-card)

---

## 1. Quick Setup

### Before the demo (do this once):

```bash
cd INF2003-Grp11
docker-compose up
```

Wait until you see:
```
ecommerce-data-loader exited with code 0
ecommerce-backend | 🚀 Starting E-Commerce Analytics Platform...
```

### What's running:

| URL | What |
|-----|------|
| `http://localhost:3000` | **Website** (open this for the demo) |
| `http://localhost:8000/docs` | **Swagger API docs** (show this to demonstrate all 18 endpoints) |

> **Pro tip:** Open the website in an **incognito/private window** to start with a clean session. Open the Swagger docs in a separate tab to reference API endpoints during the demo.

---

## 2. Demo 1: Product Browser (No Login)

**What to show:** The public product catalog.

| Step | Action | What to say |
|------|--------|-------------|
| 1 | Go to `http://localhost:3000` | "This is our e-commerce storefront. It loads 1,197 products from PostgreSQL." |
| 2 | Point out the 7 categories in the dropdown | "Products are organized into 7 categories: Beauty, Books, Electronics, Fashion, Home & Kitchen, Sports, and Toys." |
| 3 | Select "Fashion" from the dropdown, click Search | "The category filter queries PostgreSQL in real-time. Notice the URL doesn't change — this is a React SPA." |
| 4 | Type "770" in the search bar, click Search | "You can also search by product ID." |
| 5 | Click "All Categories" and Search to reset | "1,197 products across 60 pages with pagination." |
| 6 | Point out the stock quantities | "Each product shows current stock. These are enforced by PostgreSQL CHECK constraints — stock can never go below zero." |
| 7 | Note there are no "Add to Cart" buttons | "Without logging in, you can browse but not interact. This protects our APIs with JWT authentication." |

**Under the hood:** `GET /api/products/` → PostgreSQL `SELECT` with pagination and optional `WHERE category` filter.

---

## 3. Demo 2: User Registration & Login

**What to show:** JWT authentication with bcrypt password hashing.

| Step | Action | What to say |
|------|--------|-------------|
| 1 | Click "Register" in the navbar | "Let's create an account. The registration form validates inputs and stores passwords with bcrypt hashing — even we can't read them." |
| 2 | Fill in: Username: `demouser`, Email: `demo@test.com`, Display Name: `Demo User`, Password: `demo123456` | Fill all fields |
| 3 | Click "Create Account" | "Registration successful! Now we can log in." |
| 4 | You are switched to Login mode. Fill username & password, click "Sign In" | "Login returns a JWT token stored in the browser. Every subsequent API request sends this token for authentication." |
| 5 | Point out the navbar change | "Notice the navbar now shows Cart, our display name 'Demo User', and a Logout button. This is role-based — if we were an admin, we'd also see an Admin link." |

**Under the hood:** `POST /api/auth/register` → `POST /api/auth/login` → JWT returned → stored in `localStorage` → sent as `Authorization: Bearer` header on all requests.

---

## 4. Demo 3: Add to Cart & Clickstream Events

**What to show:** MongoDB Bucket Pattern recording every user action.

| Step | Action | What to say |
|------|--------|-------------|
| 1 | Click "Add to Cart" on any product | "When I click Add to Cart, a clickstream event is recorded in **MongoDB**, not PostgreSQL. This uses the Bucket Pattern — all events for this session are accumulated in one document using atomic `$push` + `$inc` operations." |
| 2 | Click "Add to Cart" on 2-3 more products | "Each click is near-instant. MongoDB handles these high-velocity writes at O(1) complexity — perfect for clickstream data." |
| 3 | Point out the toast notification | "The green toast at the top confirms each event was recorded. The toast auto-dismisses after a few seconds." |
| 4 | **Optional:** Open Swagger (`http://localhost:8000/docs`), find `GET /api/cart/session/{id}`, enter the session ID from the browser console, click Execute | "Behind the scenes, you can retrieve all events for a session via the API. Every page view, cart action, checkout, and purchase is logged." |

**Under the hood:** `POST /api/cart/event` → MongoDB `updateOne` with `$push: {events: {...}}` + `$inc: {event_count: 1}` + `upsert: true`.

---

## 5. Demo 4: Place an Order (ACID Transaction + Triggers)

**What to show:** Full PostgreSQL ACID transaction with 4 database triggers.

| Step | Action | What to say |
|------|--------|-------------|
| 1 | Click "🛒 Checkout (Sample Order)" | "Now let's place an order. This is where PostgreSQL shines." |
| 2 | Point out the success message | "Order placed successfully! But what just happened behind the scenes?" |
| 3 | **Explain the trigger cascade:** | |
| | — Trigger 1: `trg_check_stock` | "Before inserting order items, PostgreSQL checks that stock is sufficient. If it's not, the entire transaction is rejected." |
| | — Trigger 2: `trg_deduct_inventory` | "After inserting, stock quantities are automatically decremented. This happens at the database level — no application code needed." |
| | — Trigger 3: `trg_outbox_order` | "A JSON event is written to the `outbox` table. This is our CDC (Change Data Capture) mechanism." |
| | — Trigger 4: `trg_audit_order` | "Any status change is logged to the audit trail for compliance." |
| 4 | Refresh the page | "Notice the stock for the products that were ordered has decreased. This is the inventory deduction trigger at work." |
| 5 | **Optional:** Show the benchmark comparison | "We have a benchmark suite that compares PostgreSQL transactions vs MongoDB bulk inserts. PostgreSQL handles concurrent updates with row-level locking — no double-selling inventory." |

**Under the hood:** `POST /api/orders/` → PostgreSQL transaction → triggers fire → `COMMIT` (all or nothing).

---

## 6. Demo 5: Cart & Clickstream Page

**What to show:** The dedicated clickstream testing interface.

| Step | Action | What to say |
|------|--------|-------------|
| 1 | Click "Cart" in the navbar | "This is our clickstream testing page. It simulates a user browsing session." |
| 2 | Click "📄 Page View" | "Each button records a different event type. Page views are the top of the funnel." |
| 3 | Click "🛒 Add to Cart" | "Add to cart events show user intent." |
| 4 | Click "💳 Checkout" | "Checkout events indicate purchase initiation." |
| 5 | Click "✅ Purchase" | "Purchase events mark successful conversion." |
| 6 | Point out the session ID | "Every event is tied to this session ID. All 4 event types are stored in a single MongoDB document using the Bucket Pattern." |

**Under the hood:** All 4 event types recorded in MongoDB `user_sessions` via Bucket Pattern. Session ID persists in `localStorage`.

---

## 7. Demo 6: Fraud Detection

**What to show:** Cross-database fraud pipeline (MongoDB → PostgreSQL).

| Step | Action | What to say |
|------|--------|-------------|
| 1 | On the Cart page, click "🛒 Add to Cart" **rapidly — 10+ times** within a few seconds | "Now let's trigger our fraud detection system. I'm clicking Add to Cart rapidly..." |
| 2 | **After 10 clicks:** A red warning appears | "⚠️ FRAUD ALERT: Rapid cart activity — 10+ events in 60 seconds with no purchase! The system detected suspicious behavior." |
| 3 | Click a few more times | "The counter updates in real-time: 11 events, 12 events... Each click is being checked against the threshold." |
| 4 | **Explain the pipeline:** | "This is cross-database: MongoDB checks the session velocity, and when the threshold is exceeded, an alert is inserted into PostgreSQL's `alerts` table." |
| 5 | **Optional:** Go to Admin Dashboard → Alerts tab | "The alert also appears in the admin dashboard for review." |

**Under the hood:** MongoDB `user_sessions` velocity check → if `event_count >= 10` in 60 seconds with no purchase → `flagged: true` in MongoDB + `INSERT INTO alerts` in PostgreSQL.

---

## 8. Demo 7: Admin Dashboard — All Analytics

**What to show:** All 5 analytics tabs with real data from both databases.

> **Note:** You need an admin account. Log out and log in as `testuser123` / `securepass123` (or any account promoted to admin).

### 8.1 RFM Segmentation (PostgreSQL)

| Step | Action | What to say |
|------|--------|-------------|
| 1 | Click "📊 RFM Segmentation" tab | "RFM stands for Recency, Frequency, Monetary. This is a classic customer segmentation technique." |
| 2 | Point out the pie chart | "PostgreSQL computed this using CTEs (Common Table Expressions) and NTILE(4) to split all 32,537 customers into 5 segments." |
| 3 | Point out the segment breakdown | "Champions are our best customers — they buy recently, frequently, and spend a lot. Lost customers haven't purchased in a very long time." |
| 4 | Scroll to the table | "The top 15 customers are shown with their individual R, F, M scores and segment labels." |

**Under the hood:** `GET /api/analytics/rfm` → PostgreSQL CTE with `NTILE(4) OVER (...)` across all orders.

### 8.2 Funnel Analytics (MongoDB)

| Step | Action | What to say |
|------|--------|-------------|
| 1 | Click "📈 Funnel Analytics" tab | "This shows the conversion funnel — how many users progress from browsing to buying." |
| 2 | Point out the bar chart | "120,000 page views → 18,500 add to cart (15.5%) → 10,100 checkout (8.5%) → 7,500 purchases (6.3%)." |
| 3 | Point out the table | "This was computed by MongoDB using the `$facet` aggregation pipeline — 4 parallel counts in a single query." |

**Under the hood:** `GET /api/analytics/funnel` → MongoDB `$facet` aggregation on `user_sessions`.

### 8.3 Fraud Alerts

| Step | Action | What to say |
|------|--------|-------------|
| 1 | Click "🚨 Alerts" tab | "Any fraud alerts generated from the Cart page appear here. Each alert shows the customer, reason, timestamp, and acknowledgment status." |
| 2 | (If no alerts) | "If there are no alerts, go back to the Cart page and trigger the fraud detection by clicking Add to Cart 10+ times." |

### 8.4 Top Products (PostgreSQL)

| Step | Action | What to say |
|------|--------|-------------|
| 1 | Click "🏆 Top Products" tab | "Top-selling products by quantity sold, computed via PostgreSQL GROUP BY on order_items." |
| 2 | Point out the revenue column | "Notice that high sales volume doesn't always mean high revenue — some products sell many units at low prices." |

### 8.5 Market Basket (PostgreSQL)

| Step | Action | What to say |
|------|--------|-------------|
| 1 | Click "🛒 Market Basket" tab | "Market basket analysis finds products frequently bought together — like Amazon's 'Frequently Bought Together'." |
| 2 | Point out product pairs | "Products 514 and 623 were bought together 8 times. This is computed using a self-join on the order_items table in PostgreSQL." |

**Under the hood:** `GET /api/analytics/market-basket` → PostgreSQL self-join: `order_items JOIN order_items ON order_id`.

---

## 9. Demo 8: Database Reset (Optional)

**What to show:** The ability to wipe and restart from scratch.

| Step | Action | What to say |
|------|--------|-------------|
| 1 | In terminal: `docker-compose down` | "Let me show you how easy it is to reset everything." |
| 2 | `docker-compose --profile reset up reset-db` | "This wipes both databases completely — all tables in PostgreSQL, all collections in MongoDB." |
| 3 | `docker-compose up` | "Starting fresh — the data loader automatically reloads all 275,000 rows from CSV files." |
| 4 | Wait ~2 min, refresh the browser | "Everything is back to a clean state, ready for the next demo." |

---

## 10. Quick Reference Card

### Credentials

| Role | Username | Password | Notes |
|------|----------|----------|-------|
| Admin | `testuser123` | `securepass123` | Pre-promoted to admin |
| Customer | Register any new account | — | Default role is "customer" |
| Legacy | `user_1` | `password123` | From data loader (customer role) |

### Key URLs

| URL | What |
|-----|------|
| `http://localhost:3000` | Website |
| `http://localhost:3000/login` | Login page |
| `http://localhost:3000/cart` | Cart & clickstream |
| `http://localhost:3000/admin` | Admin dashboard (admin only) |
| `http://localhost:8000/docs` | Swagger API docs |
| `http://localhost:8000/api/health` | Health check JSON |

### Key Terminal Commands

| Command | Purpose |
|---------|---------|
| `docker-compose up` | Start everything |
| `docker-compose down` | Stop everything |
| `docker-compose --profile reset up reset-db` | Wipe databases |
| `docker exec -it ecommerce-backend python tests/test_suite.py` | Run 161 tests |
| `docker exec -it ecommerce-backend python benchmark/benchmark_runner.py` | Run benchmarks |
| `docker restart ecommerce-frontend` | Restart frontend |

### Feature-to-Database Mapping

| Feature | Database | Tech |
|---------|----------|------|
| Product catalog | PostgreSQL | SQLAlchemy ORM |
| Order creation | PostgreSQL | ACID transaction + 4 triggers |
| Clickstream events | MongoDB | Bucket Pattern ($push + $inc) |
| Fraud detection | Both | MongoDB check → PostgreSQL alert |
| RFM segmentation | PostgreSQL | CTE + NTILE(4) |
| Market basket | PostgreSQL | Self-join |
| Funnel analytics | MongoDB | $facet aggregation |
| Cart abandonment | MongoDB | Aggregation pipeline |
| CDC sync | Both | Outbox Pattern (trigger → poller) |
| Auth | PostgreSQL | JWT + bcrypt |

### Demo Flow (5 minutes)

1. **Show product catalog** (1 min) — Browse products, filter by category, search
2. **Register & login** (30 sec) — Create account, login, show navbar change
3. **Add to cart + checkout** (1 min) — Click Add to Cart, place sample order, explain triggers
4. **Fraud detection** (30 sec) — Rapid-fire Add to Cart 10+ times, show alert
5. **Admin dashboard** (1.5 min) — RFM pie chart, funnel bar, top products, market basket
6. **Wrap up** (30 sec) — Mention Swagger docs, test suite, Docker setup

---

*INF2003 Group 11 — Team Hanzalians — June 2026*
