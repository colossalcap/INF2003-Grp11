# Entity-Relationship Diagram — E-Commerce Analytics
## INF2003 Group 11

---

## Conceptual ER Diagram

```
┌──────────────────────────┐       ┌──────────────────────────┐
│         users            │       │        customers         │
├──────────────────────────┤       ├──────────────────────────┤
│ PK  user_id       INT    │       │ PK  customer_id   UUID   │
│     username      VARCHAR│       │     registration_date    │
│     email         VARCHAR│       │       TIMESTAMP          │
│     password_hash VARCHAR│       │     country_code  CHAR(3)│
│     display_name  VARCHAR│       │     opt_in_status BOOLEAN│
│     role          VARCHAR│       │                          │
│     created_at    TIMESTMP│      └───────────┬──────────────┘
└──────────────────────────┘                   │ 1:M
                                               │
┌──────────────────────────┐                   │
│         orders           │◄──────────────────┘
├──────────────────────────┤
│ PK  order_id      UUID   │
│ FK  customer_id   UUID   │──────┐ 1:M
│     order_date    TIMESTMP│     │
│     total_amount  DECIMAL │     │
│     status        VARCHAR │     │
└──────────────────────────┘     │
                                 │
┌──────────────────────────┐     │
│       order_items        │◄────┘
├──────────────────────────┤
│ PK  item_id       SERIAL │
│ FK  order_id      UUID   │
│ FK  product_id    VARCHAR│──────┐ M:1
│     quantity      INTEGER│     │
│ CHECK (quantity > 0)     │     │
└──────────────────────────┘     │
                                 │
┌──────────────────────────┐     │
│        products          │◄────┘
├──────────────────────────┤
│ PK  product_id    VARCHAR│
│     category      VARCHAR│
│     unit_price    DECIMAL │
│     stock_quantity INTEGER│
│ CHECK (stock >= 0)       │
└──────────────────────────┘


┌──────────────────────────┐     ┌──────────────────────────┐
│         outbox           │     │     order_audit_log      │
│   (CDC / Event Store)    │     │   (Trigger-populated)    │
├──────────────────────────┤     ├──────────────────────────┤
│ PK  event_id      SERIAL │     │ PK  audit_id      SERIAL │
│     aggregate_id  VARCHAR│     │     order_id       UUID  │
│     event_type    VARCHAR│     │     changed_by    VARCHAR│
│     payload       JSONB  │     │     field_name    VARCHAR│
│     created_at    TIMESTMP│    │     old_value      TEXT  │
│     processed     BOOLEAN│     │     new_value      TEXT  │
└──────────────────────────┘     │     changed_at    TIMESTMP│
                                 └──────────────────────────┘


┌──────────────────────────┐
│         alerts           │
│   (Fraud Detection)      │
├──────────────────────────┤
│ PK  alert_id      SERIAL │
│     customer_id   UUID   │
│     message        TEXT  │
│     alert_type    VARCHAR│
│     created_at    TIMESTMP│
│     acknowledged  BOOLEAN│
└──────────────────────────┘
```

---

## Relationship Types Demonstrated

| Relationship | Type | Tables | Implementation |
|-------------|------|--------|----------------|
| Customer → Order | **1:M** | customers → orders | FK `customer_id` in orders |
| Order → OrderItem | **1:M** | orders → order_items | FK `order_id` in order_items |
| Product → OrderItem | **1:M** | products → order_items | FK `product_id` in order_items |

---

## NoSQL Document Store (MongoDB)

```
┌──────────────────────────────────────┐
│          user_sessions               │
│        (Bucket Pattern)              │
├──────────────────────────────────────┤
│ _id:          ObjectId               │
│ customer_id:  String                 │
│ session_id:   String                 │
│ start_time:   ISODate                │
│ end_time:     ISODate                │
│ event_count:  Integer  ← $inc        │
│ flagged:      Boolean                │
│ events: [                            │
│   { action_type, product_id, ts }    │
│ ]                     ← $push        │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│       customer_order_summary         │
│         (CDC Target)                 │
├──────────────────────────────────────┤
│ customer_id:  String    (unique)     │
│ total_orders: Integer  ← $inc        │
│ total_spent:  Float    ← $inc        │
│ last_order_date: ISODate             │
│ last_updated: ISODate                │
└──────────────────────────────────────┘
```

---

## Trigger Summary

| Trigger | Fires On | Purpose |
|---------|----------|---------|
| `trg_check_stock` | BEFORE INSERT on order_items | Validates sufficient stock exists |
| `trg_deduct_inventory` | AFTER INSERT on order_items | Decrements `products.stock_quantity` |
| `trg_outbox_order` | AFTER INSERT on orders | Writes CDC event to `outbox` table |
| `trg_audit_order` | AFTER UPDATE on orders | Logs status/total changes to `order_audit_log` |

**Total: 7 relational tables + 4 MongoDB collections**
