# 🛒 INF2003 Group 11 — Project Walkthrough

**A friendly guide for anyone who wants to understand this project — no programming knowledge needed!**

---

## Table of Contents

1. [What Is This Project?](#1-what-is-this-project)
2. [The Big Picture](#2-the-big-picture)
3. [What You Need Before Starting](#3-what-you-need-before-starting)
4. [Step-by-Step: How to Start Everything](#4-step-by-step-how-to-start-everything)
5. [Loading the Sample Data](#5-loading-the-sample-data)
6. [Exploring the Website](#6-exploring-the-website)
7. [Understanding the Two Databases](#7-understanding-the-two-databases)
8. [The Cool Features (Explained Simply)](#8-the-cool-features-explained-simply)
9. [Running the Test Suite](#9-running-the-test-suite)
10. [Running the Benchmark Suite](#10-running-the-benchmark-suite)
11. [Project Folder Tour](#11-project-folder-tour)
12. [Glossary — What All Those Fancy Words Mean](#12-glossary--what-all-those-fancy-words-mean)

---

## 1. What Is This Project?

Imagine you run an online store like Amazon or Shopee. Every day, two very different things happen:

1. **People browse around** — they look at products, add things to their cart, maybe leave without buying. This happens *thousands of times per second* and each action is just a tiny log entry. Speed is everything here; you don't want your website to feel slow.

2. **People actually buy things** — money changes hands, inventory needs to be updated, receipts need to be generated. This *must* be 100% accurate. If you sell the last item in stock to two people at once, you have a disaster.

These two types of activity are so different that using a single database for both is like using a sports car to haul furniture — it can do it, but it's terrible at one of the two jobs.

**This project solves that problem.** We built a mock online store that uses:

- **PostgreSQL** (a "relational" database) for the money stuff — orders, inventory, customer accounts. It's slow but *never makes mistakes*.
- **MongoDB** (a "NoSQL" database) for the browsing stuff — every page view, every cart click. It's blazing fast and handles chaotic data beautifully.

The two databases talk to each other through a clever system called the **Outbox Pattern**, so information flows from one to the other automatically.

On top of this, we built a **website** where you can browse products, add them to a cart, place orders, and view fancy charts showing business insights (like "which products sell together?" and "which customers are our best ones?").

**This is a university group project** for the module **INF2003 Database Design & Implementation** at the Singapore Institute of Technology. Our team is **Group 11 — Team Hanzalians**.

---

## 2. The Big Picture

Here is what happens behind the scenes when you use our application:

```
┌──────────────────────────────────────────────────────┐
│                   YOUR WEB BROWSER                    │
│          (You see products, cart, charts)             │
└──────────────────────┬───────────────────────────────┘
                       │  "Show me products!"
                       │  "Place this order!"
                       ▼
┌──────────────────────────────────────────────────────┐
│                THE BACKEND (FastAPI)                  │
│     A Python program that handles all requests        │
│     and decides which database to use for each.       │
└──────────┬──────────────────────┬────────────────────┘
           │                      │
           ▼                      ▼
┌─────────────────────┐  ┌─────────────────────────────┐
│    POSTGRESQL       │  │         MONGODB              │
│  (The "careful" DB) │  │    (The "fast" DB)           │
│                     │  │                              │
│  Stores:            │  │  Stores:                     │
│  • Customer info    │  │  • Every page you visit      │
│  • Product catalog  │  │  • Every cart action         │
│  • Every order      │  │  • Session summaries         │
│  • Fraud alerts     │  │  • Funnel statistics         │
│  • Change history   │  │                              │
│                     │  │                              │
│  "I never lose      │  │  "I can handle 100,000       │
│   data or make      │  │   events per second!"        │
│   mistakes!"        │  │                              │
└─────────────────────┘  └─────────────────────────────┘
```

**The key insight:** We send each type of data to the database best suited for it. Browsing data goes to MongoDB (fast). Purchase data goes to PostgreSQL (reliable).

---

## 3. What You Need Before Starting

You only need one thing installed on your computer:

| What | Why You Need It | Where to Get It |
|------|----------------|-----------------|
| **Docker Desktop** | Runs all the databases and the website in one click | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) |

> **What is Docker?** Think of it as a "computer simulator." It lets us package our entire project — databases, website, and all — into a single file. When you run it, Docker creates a mini virtual computer on your real computer with everything pre-configured. No messy installations needed!

That's it! Docker comes with everything else bundled inside. You don't need to install Python, PostgreSQL, MongoDB, or anything else separately.

**Optional:** If you want to look at the code or make changes, you might also want:
- **VS Code** (or any text editor) — [code.visualstudio.com](https://code.visualstudio.com)
- **Python 3.11+** — only if you want to run things outside of Docker

---

## 4. Step-by-Step: How to Start Everything

### Step 1: Open a Terminal

- **On Windows:** Press the Windows key, type `PowerShell`, and press Enter.
- **On Mac:** Press `Cmd + Space`, type `Terminal`, and press Enter.

A black (or white) window with text will appear. This is where you type commands.

### Step 2: Navigate to the Project Folder

Type this and press Enter:

```bash
cd C:\Users\tdmca\OneDrive\Desktop\Database\INF2003-Grp11
```

> Replace the path with wherever you saved the project folder. If you're not sure, find the `INF2003-Grp11` folder in File Explorer, then drag and drop it into the terminal window — the path will appear automatically!

### Step 3: Start Everything

Type this one command and press Enter:

```bash
docker-compose up
```

The first time you run this, Docker will download everything it needs (this might take 5-10 minutes depending on your internet speed). You'll see a lot of text scrolling by — that's normal!

When it's done, you'll see messages like:
```
ecommerce-postgres     | database system is ready to accept connections
ecommerce-mongodb      | Waiting for connections
ecommerce-data-loader  | Loading customers → PostgreSQL ... 20000 loaded
ecommerce-data-loader  | Loading products → PostgreSQL ... 1197 loaded
ecommerce-data-loader  | Loading orders → PostgreSQL ... 53000 loaded
ecommerce-data-loader  | Loading clickstream → MongoDB ... 120000 loaded
ecommerce-data-loader exited with code 0  ← Done loading!
ecommerce-backend      | 🚀 Starting E-Commerce Analytics Platform...
ecommerce-frontend     | ➜ Local: http://localhost:3000/
```

> The `ecommerce-data-loader` runs once, loads all the data into both databases, then exits. It takes 1-2 minutes. The website won't show products until it finishes!

### Step 4: Open the Website

Open your web browser (Chrome, Edge, Firefox) and go to:

```
http://localhost:3000
```

You should see the online store with 1,197 products! 🎉

> **Also check out:** `http://localhost:8000/docs` — this is the automatic API documentation. It lists every feature our backend supports, and you can even test them right there in the browser!

### Step 5: When You're Done

To stop everything, go back to the terminal and press `Ctrl + C` (hold the Control key and press C). Wait a few seconds for everything to shut down gracefully.

To start again later, just run `docker-compose up` again — it will be much faster the second time.

---

## 5. Loading the Sample Data

**Good news — this now happens automatically!** 🎉

When you run `docker-compose up`, a special one-shot container called `data-loader` starts up right after the databases are ready. It automatically loads all the CSV files and then exits. You'll see its progress in the terminal output.

The project comes with real-world-style data in CSV files (spreadsheet-like files) inside the `data/` folder:

| File | Contains | Full Dataset | Demo Mode (Default) |
|------|----------|-------------|---------------------|
| `customers.csv` | Customer profiles | 20,000 | **2,000** |
| `products.csv` | Product catalog | 1,197 | 1,197 (all) |
| `orders.csv` | Purchase orders | 33,580 | **3,000** |
| `order_items.csv` | Items in each order | 75,000 | filtered to match orders |
| `clickstream_events.csv` | Page views & cart actions | 760,958 | **40,000** |
| `sessions.csv` | User browsing sessions | 120,000 | **10,000** |

> **Where does this data come from?** These datasets were sourced from two Kaggle datasets:
> - [E-commerce Clickstream and Transaction Dataset](https://www.kaggle.com/datasets/waqi786/e-commerce-clickstream-and-transaction-dataset) by waqi786
> - [Synthetic E-commerce Transactions + Clickstream 2020–2025](https://www.kaggle.com/datasets/wafaaelhusseini/e-commerce-transactions-clickstream) by Wafaa Elhusseini
>
> Combined and processed into 6 CSV files totaling ~275,000 rows of realistic e-commerce data.

> **What does this do?** The `data_loader.py` program reads each CSV file and inserts the data into the correct database — customer and product info goes to PostgreSQL, clickstream events go to MongoDB. By default it runs in **demo mode** which takes about **1.5 minutes**. You can watch its progress in the `docker-compose up` terminal output.
>
> **Want the full dataset?** Edit `backend/data_loader.py` and set `DEMO_MODE = False` at the top of the file. Then reset databases and rebuild:
> ```bash
> docker compose --profile reset up reset-db
> docker compose build data-loader
> docker compose up -d data-loader
> ```
> The full dataset takes ~20 minutes to load but provides 275,000+ rows for deeper analysis and benchmarking.
>
> **How we made it fast:** The loader uses three key optimizations:
> 1. **Batch MongoDB writes** — Instead of 761K individual database calls, events are grouped by session and pushed all at once using `$push: { $each: [...] }` — one DB operation per session instead of per event.
> 2. **Data sampling** — CSV files are read with row limits (`nrows` parameter) so we never load more data than needed.
> 3. **Bulk inserts** — Session documents are created with `insert_many` (10,000 at once) instead of individual upserts.

**If you ever need to reload the data manually** (or if you skipped the auto-loader by commenting it out):

```bash
docker exec -it ecommerce-backend python data_loader.py
```

> **Tip for returning users:** After your first `docker-compose up`, the data is already loaded. On subsequent starts, you can skip the data loader by commenting out the `data-loader` section in `docker-compose.yml` (add a `#` at the start of each line). This makes startup much faster.

You'll see progress messages as it loads. When it's done, the website will show real products and the analytics charts will have data to display!

---

## 6. Exploring the Website

Our website has four main pages. Here's what each one does:

### 🏠 Products Page (`/`)
The homepage shows a catalog of products. You can:
- **Scroll** through all 1,197 products (20 per page)
- **Filter** by category — click "Electronics", "Fashion", "Books", etc.
- **Search** by typing a product ID number
- **Click** "Add to Cart" on any product (this records a clickstream event in MongoDB!)

### 🛒 Cart Page (`/cart`)
Shows items you've added. Behind the scenes, every action — viewing a product, adding to cart, checking out — is silently logged to MongoDB using the **Bucket Pattern** (see Section 7).

### 📊 Admin Dashboard (`/admin`)
This is where the magic happens! The admin dashboard shows:

| Chart | What It Tells You | Database Used |
|-------|-------------------|---------------|
| **RFM Pie Chart** | Who are your best customers? (Champions, Loyal, At Risk, Lost) | PostgreSQL |
| **Funnel Bar Chart** | How many visitors convert to buyers? (120k views → 7.5k purchases) | MongoDB |
| **Market Basket Table** | Which products are often bought together? ("People who bought X also bought Y") | PostgreSQL |
| **Top Products** | What sells the most? | PostgreSQL |
| **Sales by Category** | Which category makes the most money? | PostgreSQL |
| **Fraud Alerts** | Suspicious activity detected (admin only) | Both |

> **Note:** You need to log in as an **admin** user to see the admin dashboard. Regular users can only browse and shop.

### 🔐 Login/Register (`/login`)
Create an account or sign in. The system uses **JWT tokens** (a secure digital ID card) to remember who you are. Passwords are stored scrambled (hashed) so even we can't read them.

---

## 7. Understanding the Two Databases

This is the heart of the project. Let's explain it with an analogy:

### 🏦 PostgreSQL — The Bank Vault

Imagine a bank vault. Every transaction is recorded in a ledger with strict rules:
- You can't withdraw money you don't have
- Every entry is permanent and can't be undone
- If two people try to take the last dollar at the same time, only one succeeds

That's PostgreSQL. It uses **ACID** principles:
- **A**tomicity — an order either completes fully or not at all
- **C**onsistency — data always follows the rules (e.g., stock can never go negative)
- **I**solation — two orders don't interfere with each other
- **D**urability — once saved, data is never lost

**What we store here:** Customers, products, orders, order items, user accounts, fraud alerts, audit logs.

### 🏎️ MongoDB — The High-Speed Conveyor Belt

Now imagine a factory conveyor belt. Items zoom past, and you just need to count them and note what they are. Speed matters more than perfect accuracy — if you miss one item out of a million, nobody cares.

That's MongoDB. It uses **BASE** principles:
- **B**asically **A**vailable — always responds quickly, even under heavy load
- **S**oft-state — data might be slightly out of date for a moment
- **E**ventually consistent — given enough time, everything syncs up

**What we store here:** Every page view, cart click, and browsing session. These happen thousands of times per second and don't need bank-level accuracy.

### 🔗 How They Talk: The Outbox Pattern

Here's the clever part. When someone places an order in PostgreSQL, a **trigger** (an automatic rule) writes a copy of the order to a special `outbox` table. Then, a background worker reads that outbox and updates a summary in MongoDB. This way:

- The order is processed reliably in PostgreSQL (ACID)
- MongoDB gets a denormalized copy for fast analytics
- If the sync fails, the outbox entry stays and gets retried

```
Order Placed → PostgreSQL saves it → Trigger writes to outbox → 
Background worker picks up → MongoDB summary updated
```

---

## 8. The Cool Features (Explained Simply)

### 🔫 Triggers (Automatic Rules)
We have **4 triggers** in PostgreSQL. Think of them as "if this happens, automatically do that":

| Trigger | When It Fires | What It Does |
|---------|--------------|--------------|
| **Stock Check** | Before adding an item to an order | "Is there enough stock? If not, reject the order!" |
| **Inventory Deduction** | After adding an item to an order | "Reduce the stock count by the quantity ordered." |
| **Outbox CDC** | After creating an order | "Write a copy of this order to the outbox for MongoDB sync." |
| **Audit Log** | When an order status changes | "Record who changed what and when." |

### 🔍 Analytics (Business Insights)

**RFM Segmentation** — Classifies every customer into one of 5 groups:
- 🏆 **Champions** — Buy often, spend a lot, bought recently
- 💛 **Loyal Customers** — Buy regularly
- 🌱 **Potential Loyalists** — New but promising
- ⚠️ **At Risk** — Haven't bought in a while
- 💀 **Lost** — Haven't bought in a very long time

**Market Basket Analysis** — "People who bought Product A also bought Product B." Used for product recommendations (like Amazon's "Frequently Bought Together").

**Funnel Analytics** — Tracks the journey from visitor to buyer:
```
120,000 page views → 18,568 add to cart → 10,134 checkout → 7,523 purchases
     100%          →      15.5%          →     8.5%        →     6.3%
```
Each step shows where you're losing customers.

**Cart Abandonment** — Finds sessions where someone added items to their cart but never checked out. These are lost sales opportunities.

### 🚨 Fraud Detection
If someone adds items to their cart **10+ times in 60 seconds** without ever purchasing, the system flags it as suspicious and creates an alert. This runs in MongoDB (checking the session velocity) and writes alerts to PostgreSQL.

### 🧪 Test Suite
We have a **161-test automated test suite** that verifies every single feature works correctly. It tests all API endpoints, both databases, all 4 triggers, authentication, error handling, and more. See Section 9 for how to run it.

### ⚡ Benchmark Suite
Compares the performance of PostgreSQL vs MongoDB on different types of operations:
- **MongoDB Bulk Insert** — 10,000 clickstream events (MongoDB wins — it's designed for this)
- **PostgreSQL Hotspot** — 200 concurrent inventory updates (PostgreSQL handles contention well)
- **PostgreSQL 5-Table JOIN** — Complex query across orders, customers, items, products (relational strength)
- **MongoDB Aggregation** — Equivalent of a complex GROUP BY query (NoSQL approach)

Results are saved as charts in `backend/benchmark/plots/`.

---

## 9. Running the Test Suite

We've built a comprehensive test that checks every part of the project. To run it:

```bash
docker exec -it ecommerce-backend python tests/test_suite.py
```

You'll see output like this:

```
████████████████████████████████████████████████████████████
█  INF2003 Group 11 — Comprehensive Test Suite
█  2026-06-29 07:36:15
████████████████████████████████████████████████████████████

════════════════════════════════════════════════════════════
  1. HEALTH CHECKS
════════════════════════════════════════════════════════════
  ✅ Root health check [HTTP 200]
  ✅ Status is 'running'
  ✅ Detailed health check [HTTP 200]
  ✅ PostgreSQL healthy
  ✅ MongoDB healthy
  ... (and 156 more tests)

════════════════════════════════════════════════════════════
  RESULTS
════════════════════════════════════════════════════════════
  ✅ Passed:  161/161
  ❌ Failed:  0/161
  ⏱️  Time:    7.08s
════════════════════════════════════════════════════════════

  🎉 ALL TESTS PASSED!
```

The test suite covers:

| Section | What It Tests | # Tests |
|---------|--------------|---------|
| Health Checks | All services running, databases connected | 7 |
| Authentication | Register, login, security, error handling | 12 |
| Products | Catalog, pagination, search, categories | 30 |
| Cart & Clickstream | All event types, MongoDB bucket pattern | 16 |
| Orders | ACID transactions, stock validation, triggers | 18 |
| Analytics | RFM, funnel, market basket, top products | 24 |
| Admin Analytics | Alerts, audit trail, role-based access | 7 |
| Trigger Verification | All 4 PostgreSQL triggers confirmed | 10 |
| MongoDB Verification | Collections, indexes, documents | 10 |
| Error Handling | Invalid inputs, missing auth, edge cases | 6 |

---

## 10. Running the Benchmark Suite

To measure and compare database performance:

```bash
docker exec -it ecommerce-backend python benchmark/benchmark_runner.py
```

This generates charts in `backend/benchmark/plots/benchmark_results.png` showing:
- MongoDB vs PostgreSQL write speed
- PostgreSQL JOIN performance
- MongoDB aggregation pipeline speed

---

## 11. Project Folder Tour

Here's what every folder and important file does — explained in plain English:

```
INF2003-Grp11/
│
├── docker-compose.yml          ← The "master switch" — one command starts everything
├── README.md                   ← Technical overview (you're reading the friendly version!)
├── walkthrough.md              ← THIS FILE — the comprehensive guide
│
├── data/                       ← Raw data files (spreadsheets)
│   ├── customers.csv           ← 20,000 customer profiles
│   ├── products.csv            ← 1,197 products across 7 categories
│   ├── orders.csv              ← 53,000 purchase orders
│   ├── order_items.csv         ← Which products are in each order
│   ├── clickstream_events.csv  ← 120,000 page views and cart actions
│   └── sessions.csv            ← 27,500 browsing sessions
│
├── backend/                    ← The "brain" — all the server-side logic
│   ├── Dockerfile              ← Instructions for building the backend container
│   ├── requirements.txt        ← List of Python libraries we use
│   ├── main.py                 ← The starting point — launches the API server
│   ├── config.py               ← Settings (database addresses, passwords, etc.)
│   ├── triggers.sql            ← 4 automatic PostgreSQL rules (stock, inventory, outbox, audit)
│   ├── data_loader.py          ← Reads CSV files and fills the databases
│   │
│   ├── api/                    ← The "front desk" — handles incoming web requests
│   │   ├── auth.py             ← Login, register, password security
│   │   ├── products.py         ← Product catalog (list, search, filter)
│   │   ├── cart.py             ← Shopping cart & clickstream tracking
│   │   ├── orders.py           ← Placing orders (with ACID guarantees)
│   │   └── analytics.py        ← RFM, funnel, market basket, alerts, audit
│   │
│   ├── models/                 ← Blueprints for how data is structured
│   │   ├── relational.py       ← PostgreSQL table definitions (8 tables)
│   │   └── nosql_schemas.py    ← MongoDB document structure definitions
│   │
│   ├── services/               ← The "engine room" — heavy lifting logic
│   │   ├── relational_service.py  ← Complex SQL queries (RFM, market basket)
│   │   ├── nosql_service.py       ← MongoDB operations (bucket, funnel, fraud)
│   │   └── sync_service.py        ← Outbox/CDC background processor
│   │
│   ├── tests/                  ← Automated testing suite
│   │   └── test_suite.py       ← 161 tests covering every feature
│   │
│   └── benchmark/              ← Performance measurement tools
│       ├── benchmark_runner.py ← Runs speed tests on both databases
│       └── plots/              ← Generated performance charts
│
├── frontend/                   ← The "face" — what you see in the browser
│   ├── Dockerfile              ← Instructions for building the frontend container
│   ├── package.json            ← List of JavaScript libraries we use
│   ├── vite.config.js          ← Build tool configuration
│   └── src/
│       ├── App.jsx             ← Main application layout & navigation
│       ├── api.js              ← Functions that talk to the backend
│       ├── index.css           ← Styling (colors, fonts, layout)
│       └── components/
│           ├── Login.jsx       ← Login & registration page
│           ├── ProductList.jsx ← Product catalog with search & filters
│           ├── Cart.jsx        ← Shopping cart interface
│           └── AdminDashboard.jsx ← Charts & analytics dashboard
│
└── docs/                       ← Written reports and documentation
    ├── ER_Diagram.md           ← Visual map of database relationships
    ├── G11_Progress_Report.md  ← Mid-project progress report
    └── G11_Final_Report.md     ← Final submission report
```

---

## 12. Glossary — What All Those Fancy Words Mean

| Term | Plain English |
|------|--------------|
| **ACID** | A set of rules ensuring database transactions are reliable. Think: "bank-level accuracy." |
| **API** | "Application Programming Interface" — a way for programs to talk to each other. Our website talks to our backend through the API. |
| **BASE** | A more relaxed set of rules for databases that prioritize speed over perfect accuracy. Think: "good enough, very fast." |
| **Bucket Pattern** | A MongoDB technique where related events are grouped together in one document. Like putting all your receipts from one shopping trip in the same envelope. |
| **CDC** | "Change Data Capture" — automatically copying data changes from one database to another. Our outbox pattern implements this. |
| **Clickstream** | The trail of digital footprints you leave as you browse a website — every page view, every click. |
| **Container** | A lightweight virtual computer that packages an application with everything it needs to run. Docker creates these. |
| **CSV** | "Comma-Separated Values" — a simple spreadsheet format. Each line is a row, commas separate columns. |
| **CTE** | "Common Table Expression" — a temporary named result in SQL. Like a sticky note you write a calculation on, then refer to by name. |
| **Docker** | A tool that lets you run applications in isolated "containers." Like a shipping container for software. |
| **Docker Compose** | A tool that starts multiple Docker containers together. One command starts our whole project. |
| **$facet** | A MongoDB aggregation stage that runs multiple analyses in parallel. Like having multiple analysts each looking at different aspects of the same data simultaneously. |
| **FK (Foreign Key)** | A column that links one table to another. Like a "See Also" reference in a book. |
| **JSON/JSONB** | A flexible data format that looks like `{"name": "John", "age": 30}`. JSONB is PostgreSQL's optimized version. |
| **JWT** | "JSON Web Token" — a secure digital ID card. After you log in, the server gives you a JWT, and you show it with every request to prove who you are. |
| **Market Basket** | Analysis that finds products frequently bought together. "Customers who bought bread also bought butter." |
| **NoSQL** | "Not Only SQL" — databases that don't use the traditional table-with-rows format. MongoDB is a NoSQL database. |
| **NTILE** | A SQL function that divides rows into equal-sized buckets. Used in RFM to split customers into 4 groups. |
| **ORM** | "Object-Relational Mapping" — a tool that lets programmers work with databases using their programming language instead of writing SQL. SQLAlchemy is our ORM. |
| **Outbox Pattern** | A technique where database changes are written to a special "outbox" table, then a separate process picks them up and syncs them elsewhere. Like a company's outgoing mail tray. |
| **PK (Primary Key)** | A unique identifier for each row in a table. Like a NRIC or passport number. |
| **Polyglot Persistence** | Using different types of databases for different types of data. Like using both a filing cabinet and a whiteboard — each for what it does best. |
| **RFM** | "Recency, Frequency, Monetary" — a method for rating customers. How recently did they buy? How often? How much did they spend? |
| **SQL** | "Structured Query Language" — the language used to talk to relational databases like PostgreSQL. |
| **Trigger** | An automatic rule in a database. "When X happens, automatically do Y." |
| **TTL Index** | "Time To Live" — a MongoDB feature that automatically deletes documents after a certain time. Like setting an expiration date on food. |
| **UUID** | "Universally Unique Identifier" — a long random ID that is guaranteed to be unique across the entire world. Like `550e8400-e29b-41d4-a716-446655440000`. |

---

## ❓ Frequently Asked Questions

**Q: I see an error when running `docker-compose up` — "port is already allocated."**
A: Something else on your computer is using port 5432, 27017, 8000, or 3000. Stop that other program first, or change the ports in `docker-compose.yml`.

**Q: The website loads but shows no products.**
A: You need to load the sample data first. See Section 5 above.

**Q: I can't log in.**
A: Make sure you've registered first. If the data loader ran, try username `admin` — check the data loader output for the default password. Or register a new account at `/login`.

**Q: The admin dashboard says "Access Denied."**
A: Only admin users can access it. Your account has the "customer" role. Create a new account and ask your team lead to promote it to admin, or use an existing admin account from the data loader.

**Q: How do I reset everything and start over?**
A: You have two options:

**Option 1: Reset databases only (keeps Docker images, faster)**
```bash
docker-compose down                      # Stop everything
docker-compose --profile reset up reset-db   # Wipe both databases
docker-compose up                        # Fresh start (auto-loads data)
```

**Option 2: Nuclear reset (wipes everything including Docker volumes)**
```bash
docker-compose down -v    # Stop everything and delete all data
docker-compose up         # Start fresh (auto-loads data)
```

**Q: The tests fail with "Connection refused."**
A: Make sure `docker-compose up` is running in another terminal first. The tests need the backend to be running.

**Q: Where do the charts and graphs come from?**
A: The admin dashboard uses **Recharts**, a JavaScript charting library that draws pie charts, bar charts, and tables from the data our backend API returns.

---

## 📞 Need Help?

If something doesn't work:
1. Check that Docker Desktop is running (look for the whale icon in your taskbar)
2. Make sure all 4 containers are up: `docker ps` should show `ecommerce-postgres`, `ecommerce-mongodb`, `ecommerce-backend`, and `ecommerce-frontend`
3. Run the test suite: `docker exec -it ecommerce-backend python tests/test_suite.py` — it will tell you exactly what's working and what's not
4. Check the container logs: `docker logs ecommerce-backend`

---

*This walkthrough was written for the INF2003 Group Project — Group 11 (Team Hanzalians). Last updated: June 2026.*
