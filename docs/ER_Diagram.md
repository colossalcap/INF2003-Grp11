# BookHive — Entity-Relationship Diagram (ERD)
## INF2003 Group 11

---

## Conceptual ER Diagram

```
┌──────────────────────┐       ┌──────────────────────┐
│       authors        │       │     categories       │
├──────────────────────┤       ├──────────────────────┤
│ PK  author_id   INT  │       │ PK  category_id INT  │
│     name        VARCHAR│      │     name       VARCHAR│
│     biography   TEXT  │       │     description TEXT  │
│     birth_date  DATE  │       │ FK  parent_category_│
│     nationality VARCHAR│      │     id          INT  │
│     created_at  DATETIME│     │                      │
└──────────┬───────────┘       └──────────┬───────────┘
           │ M:M                          │ M:M
           │                              │
┌──────────▼──────────────────────────────▼───────────┐
│                book_authors / book_categories        │
│  (Junction Tables — resolving M:M relationships)     │
├─────────────────────────────────────────────────────┤
│  PK,FK  book_id      INT                             │
│  PK,FK  author_id    INT   (or category_id)          │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                     books                            │
├─────────────────────────────────────────────────────┤
│ PK  book_id          INT                            │
│     isbn             VARCHAR(13)  UNIQUE            │
│     title            VARCHAR(255)                   │
│     publisher        VARCHAR(100)                   │
│     publication_year INTEGER                        │
│     page_count       INTEGER                        │
│     language         VARCHAR(30)                    │
│     description      TEXT                            │
│     cover_url        VARCHAR(255)                   │
│     average_rating   DECIMAL(3,2)  ← TRIGGER        │
│     rating_count     INTEGER       ← TRIGGER        │
│     created_at       DATETIME                        │
└──────────────────────┬──────────────────────────────┘
                       │ 1:M
                       │
┌──────────────────────▼──────────────────────────────┐
│                    reviews                           │
├─────────────────────────────────────────────────────┤
│ PK  review_id        INT                            │
│ FK  user_id          INT  NOT NULL                  │
│ FK  book_id          INT  NOT NULL                  │
│     rating           INT  CHECK (1-5)               │
│     title            VARCHAR(200)                   │
│     body             TEXT                            │
│     spoiler_alert    BOOLEAN                        │
│     helpful_count    INTEGER                        │
│     created_at       DATETIME                        │
│     updated_at       DATETIME  ← TRIGGER            │
│ UNIQUE (user_id, book_id)                            │
└─────────────────────────────────────────────────────┘
                       │ M:1
                       │
┌──────────────────────▼──────────────────────────────┐
│                     users                            │
├─────────────────────────────────────────────────────┤
│ PK  user_id          INT                            │
│     username         VARCHAR(50)  UNIQUE            │
│     email            VARCHAR(100) UNIQUE            │
│     password_hash    VARCHAR(255)                   │
│     display_name     VARCHAR(100)                   │
│     bio              TEXT                            │
│     avatar_url       VARCHAR(255)                   │
│     role             VARCHAR(20)  DEFAULT 'reader'  │
│     created_at       DATETIME                        │
│     last_login       DATETIME                        │
└─────────────────────────────────────────────────────┘
```

---

## Relationship Types Demonstrated

| Relationship | Type | Tables Involved | Implementation |
|-------------|------|----------------|----------------|
| User → Review | **1:M** | users → reviews | FK `user_id` in reviews |
| Book → Review | **1:M** | books → reviews | FK `book_id` in reviews |
| Book ↔ Author | **M:M** | books ↔ authors | Junction table `book_authors` |
| Book ↔ Category | **M:M** | books ↔ categories | Junction table `book_categories` |
| Category → Category | **1:M (self-referencing)** | categories → categories | FK `parent_category_id` |

---

## Key Design Decisions

1. **Why junction tables for M:M?** Books can have multiple authors (anthologies) and multiple categories (cross-genre). Junction tables are the only normalized way to represent this in a relational model.

2. **Why `average_rating` is stored (denormalized)?** It's updated via triggers on the `reviews` table. This avoids computing AVG() on every page load. It's a classic read-optimization trade-off.

3. **Why `parent_category_id` is self-referencing?** Enables hierarchical categories (e.g., Fiction → Fantasy → Epic Fantasy). This demonstrates recursive/hierarchical data modeling.

4. **Why UNIQUE(user_id, book_id) on reviews?** Prevents a user from reviewing the same book twice.

5. **Referential Integrity:** All FKs use `ON DELETE CASCADE` so that deleting a user or book cleans up related records automatically.

---

## Cardinality Summary

```
users ──────< reviews >────── books
 1                  M        1                  M
 │                           │
 │                           ├──────< book_authors >────── authors
 │                           │        M              M
 │                           │
 │                           └──────< book_categories >── categories
 │                                    M                  M
 │                                                       │
 │                              parent_category_id ──────┘
 │                              (self-referencing 1:M)
```

**Total: 5 entity tables + 2 junction tables = 7 tables**
