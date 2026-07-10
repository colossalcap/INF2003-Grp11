# 🎬 INF2003 Group 11 — Live Demo Script (Single Presenter)

**Duration:** ~4 minutes 30 seconds
**Presenter:** 1 person (any team member)
**Format:** Screen recording — no slides, face-cam optional
**Context:** This demo plays at the END of the presentation, after all slides have been shown by the rest of the team.

---

## 🖥️ PRE-DEMO SETUP (Day Before Recording)

- [ ] Run `docker compose down -v && docker compose up --build` to start with fresh databases
- [ ] Wait for the data loader container to exit: run `docker ps -a --filter name=data-loader` and confirm `Exited (0)`
- [ ] Open Chrome in incognito/private mode (clean slate — no saved logins, no autofill)
- [ ] Pre-open these browser tabs (don't show them yet):
  - Tab 1: `http://localhost:3000` (frontend — product catalog)
  - Tab 2: `http://localhost:8000/docs` (Swagger API docs)
- [ ] Pre-open a terminal window at the project root showing `docker compose up` output
- [ ] Close all unnecessary apps, enable Do Not Disturb
- [ ] Set screen resolution to 1920×1080, browser zoom to 100%
- [ ] Have a stopwatch/timer visible to pace yourself

---

## 🎞️ THE DEMO

---

### ⏱️ [0:00 – 0:20] — DOCKER & SYSTEM STARTUP

**ON SCREEN:** Terminal window showing the `docker compose up` output (already running)

```
🎤 "Alright, let me show you the platform in action.

Our entire stack runs in Docker — five containers started with a single 
command: docker compose up. You can see the data loader has already 
finished — 2,000 customers, 1,197 products, 3,000 orders loaded into 
PostgreSQL, and 40,000 clickstream events loaded into MongoDB."

"All automatic. No manual setup needed."
```

**ACTIONS:**
- [x] Switch from slides to terminal
- [x] Point cursor to each line in the data loader output as you mention it:
  - `[OK] Loaded 2000 customers into PostgreSQL.`
  - `[OK] Loaded 1197 products into PostgreSQL.`
  - `[OK] Loaded 3000 orders into PostgreSQL.`
  - `[OK] Loaded 40000 clickstream events across 6354 sessions.`
  - `[OK] Data loading complete!`

> 💡 **TIP:** Scroll the terminal so these 5 lines are all visible together. No need to scroll during the demo — just point.

---

### ⏱️ [0:20 – 1:00] — BROWSE PRODUCTS, SEARCH & FILTER

**ON SCREEN:** Switch to browser Tab 1 — `http://localhost:3000` (product catalog)

```
🎤 "Let's open the frontend."

[SWITCH to browser — product catalog is visible]

"Here's our product catalog. 1,197 products across seven categories — 
Electronics, Fashion, Beauty, Books, Home and Kitchen, Sports, and Toys. 
Each product shows its name, category, unit price, and current stock level."

[SCROLL down slowly through ~2 pages of products]

"The stock badges are colour-coded — green for healthy, orange for 
moderate, red for low. These values come directly from PostgreSQL."

"Let me filter by category. I'll select 'Electronics'."

[CLICK category dropdown → Select "Electronics"]

"Now only electronics products. The URL updated with a query parameter — 
the backend is querying PostgreSQL with a WHERE clause on the indexed 
category column."

"Let me search for something specific."

[CLICK search box → type "SSD" → press Enter]

"We support search by product ID or name using PostgreSQL's ILIKE operator."

[POINT to search results briefly]

"Back to the full catalog."

[CLICK "All Categories" in the dropdown]
```

**ACTIONS:**
- [x] Switch to browser — product catalog at `http://localhost:3000`
- [x] Scroll down slowly through ~2 pages of products
- [x] Point cursor at stock badges (green/orange/red)
- [x] Click category dropdown → Select "Electronics"
- [x] Click search box → type `SSD` → press Enter
- [x] Click "All Categories" in dropdown to reset

---

### ⏱️ [1:00 – 1:40] — REGISTER, LOGIN & CART

**ON SCREEN:** Browser — still on product page

```
🎤 "To use the cart and place orders, we need to be logged in. Let me 
register a new account."

[CLICK "Register" in the nav bar]

"I'll use username 'demo_user', email 'demo@example.com', password 
'test1234'."

[TYPE: demo_user → Tab → demo@example.com → Tab → test1234]
[CLICK "Create Account"]

"Done. Behind the scenes, the backend hashed our password with bcrypt, 
created a user record, and automatically created a linked customer 
record in PostgreSQL — connected through a foreign key. We received a 
JWT token and we're now logged in."

[POINT to nav bar — now shows "Cart" and display name]

"Now let's add some items to the cart."

[SCROLL to find a product — the SSD from earlier works well]
[CLICK "Add to Cart"]

"You see the toast notification. But every cart click is also recorded 
as a clickstream event in MongoDB using the Bucket Pattern. Each session 
accumulates events in a single document using atomic dollar-push and 
dollar-inc operations — O of 1 complexity."

"Let me add two more items."

[CLICK "Add to Cart" on a second product]
[CLICK "Add to Cart" on a third product]

[CLICK the "Cart" link in the nav bar]

"Three items in the cart. Let's place the order."

[CLICK "Place Order"]"
```

**ACTIONS:**
- [x] Click "Register" in nav bar
- [x] Type username: `demo_user`
- [x] Type email: `demo@example.com`
- [x] Type password: `test1234`
- [x] Click "Create Account"
- [x] Point to nav bar — now shows "Cart" and display name
- [x] Click "Add to Cart" on a product → see toast
- [x] Click "Add to Cart" on second product
- [x] Click "Add to Cart" on third product
- [x] Click "Cart" in nav bar
- [x] Click "Place Order"

---

### ⏱️ [1:40 – 2:25] — ORDER CONFIRMATION & TRIGGER CASCADE

**ON SCREEN:** Browser — order confirmation page

```
🎤 "Order confirmed. But what happened behind the scenes is the 
important part."

[POINT to order details: order ID, status "confirmed", total, items]

"When I clicked 'Place Order', the backend executed a multi-table 
PostgreSQL insert inside a single ACID transaction. Four database 
triggers fired automatically — all within that same transaction."

[COUNT on fingers]

"One — a BEFORE trigger checked stock availability. Two — an AFTER 
trigger deducted inventory. Three — another AFTER trigger wrote a JSON 
event to the outbox table for cross-database sync. Four — an audit 
trigger logged the change."

"If ANY of these had failed, the ENTIRE transaction would have rolled 
back. That's ACID — all or nothing."

[SWITCH to terminal — show backend logs]

"Here are the backend logs. You can see the outbox processor — it picks 
up those JSON events and syncs denormalized summaries to MongoDB using 
idempotent dollar-inc operations."

[POINT to outbox messages: `[OK] Synced order to MongoDB for customer ...`]

"This is the Outbox Pattern — cross-database Change Data Capture without 
Kafka, without Debezium — just PostgreSQL triggers and an async Python 
poller."

[SWITCH back to browser]
[CLICK "Products" in nav bar]
[SCROLL to find a product we bought]

"And notice — the stock quantity decreased. The inventory deduction 
trigger fired automatically."
```

**ACTIONS:**
- [x] Order confirmation is visible — point to order ID, status, total
- [x] Count through 4 triggers on fingers while speaking
- [x] Switch to terminal
- [x] Point to outbox sync messages:
  - `[OUTBOX] Processed 50 outbox events.`
  - `[OK] Synced order to MongoDB for customer ...`
- [x] Switch back to browser
- [x] Click "Products" in nav bar
- [x] Find a product we bought → point to decreased stock

> ⚠️ **NOTE:** If outbox messages aren't visible in the most recent terminal output, scroll up slightly. The poller runs every 5 seconds so there will be messages from the data loader's batch. Say "the outbox poller runs every 5 seconds — here are the sync messages from earlier orders" if needed.

---

### ⏱️ [2:25 – 3:10] — FRAUD DETECTION

**ON SCREEN:** Browser — product page (still logged in as demo_user)

```
🎤 "Now let me show you fraud detection."

"Our system monitors session velocity. If a single user clicks 'add to 
cart' ten or more times within 60 seconds without completing a purchase, 
the system flags the session."

"I'm going to rapidly add items now."

[CLICK "Add to Cart" on 10–12 different products rapidly]
[COUNT under your breath as you click: "One, two, three, four, five, 
six, seven, eight, nine, ten, eleven..."]

[FRAUD ALERT TOAST APPEARS]

"There it is. 'Fraud Alert: Rapid cart activity — eleven events in 60 
seconds with no purchase.'"

"What happened? The backend queried MongoDB for this session's events 
within the last 60 seconds. It found more than ten 'add to cart' actions 
with no purchase event. It then flagged the session in MongoDB AND 
simultaneously inserted an alert into PostgreSQL's alerts table."

"Cross-database coordination — MongoDB detects the velocity pattern, 
PostgreSQL stores the evidence permanently."
```

**ACTIONS:**
- [x] Rapidly click "Add to Cart" on 10–12 different products (under 60 seconds)
- [x] Count clicks out loud
- [x] After 10th-11th click, fraud alert toast appears
- [x] Point to the toast → read the message aloud

> ⚠️ **CRITICAL:** Practice this sequence at least 5 times before recording. Click deliberately — not too fast (missing clicks) and not too slow (exceeding the 60-second window). The default threshold is 10 events in 60 seconds. If the toast doesn't appear after 12 clicks, say "If I kept going, the system would flag this session" and move on. Have a screenshot of a triggered alert as backup.

---

### ⏱️ [3:10 – 4:00] — ADMIN DASHBOARD & ANALYTICS

**ON SCREEN:** Browser — log out of demo_user, log in as admin

```
🎤 "Finally, the admin dashboard. I'll switch to our pre-loaded admin 
account."

[OPEN a new incognito window — or a different browser like Firefox]

[Navigate to http://localhost:3000/login]

"I'll log in as 'user_1' — this account was granted admin privileges 
by the data loader. Password is 'password123'."

[TYPE: user_1 → Tab → password123]
[CLICK "Sign In"]

[REDIRECTED to /admin]

"The admin dashboard is restricted to users with the admin role."

"Summary cards at the top — customers analyzed, page views, fraud alerts, 
product affinity pairs."

**[CLICK "📊 RFM Segmentation" tab]**

"Our RFM analysis classifies every customer into five segments using 
a two-stage Common Table Expression with the NTILE window function — 
pure PostgreSQL."

**[CLICK "📈 Funnel Analytics" tab]**

"The conversion funnel — page views to add-to-cart to checkout to 
purchase — computed by MongoDB's dollar-facet aggregation pipeline. 
Four parallel counts in a single database pass. Classic funnel shape."

**[CLICK "🛒 Market Basket" tab]**

"Market basket analysis — a self-join on order_items revealing which 
products are bought together. The same technique Amazon uses for 
recommendations."

**[CLICK "🚨 Alerts" tab]**

"And the fraud alert I triggered moments ago — now persisted in 
PostgreSQL for audit compliance."
```

**ACTIONS:**
- [x] Open new browser window (or different browser)
- [x] Go to `http://localhost:3000/login`
- [x] Type username: `user_1`, password: `password123`
- [x] Click "Sign In" → redirected to `/admin`
- [x] Click "📊 RFM Segmentation" tab → show pie chart, name segments
- [x] Click "📈 Funnel Analytics" tab → show bar chart
- [x] Click "🛒 Market Basket" tab → show top product pair
- [x] Click "🚨 Alerts" tab → point to the fraud alert

> 💡 **TIP:** If any chart says "Loading analytics data..." for more than 2 seconds, say "loading from our dual-database backend" and let it finish. All charts will have data because the data loader pre-populated 3,000 orders and 40,000 clickstream events.

---

### ⏱️ [4:00 – 4:15] — API SWAGGER DOCS

**ON SCREEN:** Switch to browser Tab 2 — `http://localhost:8000/docs`

```
🎤 "One more thing — FastAPI auto-generates interactive Swagger docs."

[SWITCH to browser tab showing Swagger UI]

"Twenty endpoints across five categories. Let me show you the products 
endpoint."

[SCROLL to "Products" → click "GET /api/products/" to expand]
[CLICK "Try it out"]
[CLICK "Execute"]

"1,197 products returned as JSON — paginated, with all fields. The 
frontend you saw earlier never touches the databases directly. Everything 
goes through this REST API."
```

**ACTIONS:**
- [x] Switch to `http://localhost:8000/docs`
- [x] Scroll to "Products" section
- [x] Click `GET /api/products/` → expand
- [x] Click "Try it out"
- [x] Click "Execute" → show JSON response briefly
- [x] Point to total count in response

---

### ⏱️ [4:15 – 4:30] — WRAP-UP

**ON SCREEN:** Stay on whatever page you're on

```
🎤 "So to recap: we browsed a catalog of 1,197 products with search, 
filter, and pagination — all from PostgreSQL. We registered, added 
items to cart — with every action logged to MongoDB using the Bucket 
Pattern. We placed an order through a four-trigger ACID cascade. The 
Outbox Pattern synchronized that order from PostgreSQL to MongoDB 
automatically. We triggered a real-time fraud alert with cross-database 
coordination. We explored an admin dashboard with RFM, funnel, and 
market basket analytics. And behind all of this — a 161-test automated 
suite with 100% pass rate."

"Thank you."
```

**ACTIONS:**
- [x] No clicks — just look at camera and deliver the recap
- [x] Smile

**[END OF DEMO]**

---

## 📋 POST-RECORDING CHECKLIST

- [ ] Demo section is 4–5 minutes. Trim if over.
- [ ] Screen capture is 1920×1080, text clearly readable
- [ ] No background noise, notifications, or cursor distractions
- [ ] Cursor movement is deliberate — point, don't wave
- [ ] Audio is clear and well-paced
- [ ] Export the complete video (slides + demo) as MP4 (H.264), 1080p, 30fps
- [ ] File name: `G11_Video.mp4`
- [ ] Upload to LMS Dropbox before deadline (Mon Jul 13, 2026)

---

## 🎯 QUICK TIPS

| Tip | Why |
|-----|-----|
| **Practice the fraud clicks 5+ times** | Hardest part — 10+ clicks in 60 seconds. Missing the window means losing the best demo moment. |
| **Pre-warm the browser** | Load all pages beforehand so they're cached and render instantly during recording. |
| **Count the triggers on fingers** | Visual reinforcement for the 4-trigger cascade. Audiences remember this. |
| **Don't rush** | 4.5 minutes is plenty. Speak at conversation pace. Leave half-second pauses between sections. |
| **Cursor discipline** | Move mouse to what you're talking about. Point precisely. Don't circle or wiggle. |
| **Backup plan** | If anything breaks, have screenshots ready. "Here's what it looks like when running..." |

---

*End of Demo Script — INF2003 Group 11, Team Hanzalians*
