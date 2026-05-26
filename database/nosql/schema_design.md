# NoSQL Database Schema Design — BookHive
## INF2003 Group 11

---

## 1. Design Rationale

We chose **MongoDB** (document-oriented NoSQL) for the following reasons:

| Consideration | Rationale |
|---------------|-----------|
| **Flexible Schema** | Book metadata varies wildly across genres (awards, editions, translations). A rigid relational schema would require excessive ALTER TABLE operations. |
| **Read-Heavy Workload** | Reading lists, activity logs, and review sentiments are read more often than written. MongoDB's denormalized documents optimize read performance. |
| **Embedded Documents** | A user's reading list naturally embeds book references — no need for JOINs. |
| **High Write Volume** | Activity logs can be written asynchronously without locking concerns typical in relational DBs. |
| **Scalability** | MongoDB's horizontal sharding supports future growth in user logs and metadata. |

### Why NOT a Relational DB for These Components?

- **Reading Lists**: Each user may have arbitrary list structures (`want-to-read`, `currently-reading`, custom shelves). Modeling this relationally requires a polymorphic junction table or EAV pattern, both of which are painful.
- **Book Metadata**: Fields like `awards`, `editions`, and `translations` are sparse and inconsistent across books. A document model naturally accommodates optional nested arrays.
- **Activity Logs**: High-insert, append-only data that rarely needs JOINs. Time-series data fits MongoDB's capped collections or time-to-live (TTL) indexes.

---

## 2. Collection Schemas

### 2.1 `reading_lists` Collection

Stores user-created reading lists (shelves).

```json
{
  "_id": "ObjectId",
  "user_id": 1,
  "list_name": "Want to Read",
  "description": "Books I plan to read this year",
  "is_public": true,
  "books": [
    {
      "book_id": 3,
      "title": "The Lord of the Rings",
      "isbn": "9780547928227",
      "added_at": "2026-05-20T10:30:00Z",
      "notes": "Recommended by Alice"
    }
  ],
  "created_at": "2026-01-15T08:00:00Z",
  "updated_at": "2026-05-20T10:30:00Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | Integer | FK reference to `users.user_id` in SQL |
| `list_name` | String | Name of the reading list |
| `books` | Array of Embedded Docs | Books in this list with metadata |
| `books[].book_id` | Integer | FK reference to `books.book_id` in SQL |
| `books[].notes` | String | User's personal notes about this book |
| `is_public` | Boolean | Whether others can view this list |

**Indexes:**
- `{ user_id: 1, list_name: 1 }` — unique compound index (one list name per user)
- `{ "books.book_id": 1 }` — find all lists containing a specific book

### 2.2 `review_sentiments` Collection

Stores NLP-based sentiment analysis of reviews for trend tracking.

```json
{
  "_id": "ObjectId",
  "review_id": 1,
  "book_id": 1,
  "sentiment_score": 0.85,
  "sentiment_label": "positive",
  "keywords": ["magical", "timeless", "classic", "world-building"],
  "language": "en",
  "analyzed_at": "2026-05-21T12:00:00Z"
}
```

**Indexes:**
- `{ review_id: 1 }` — unique (one analysis per review)
- `{ book_id: 1, sentiment_label: 1 }` — aggregate sentiment by book
- `{ analyzed_at: -1 }` — TTL index (auto-delete after 1 year)

### 2.3 `book_metadata` Collection

Stores flexible, extensible book metadata not suitable for rigid relational columns.

```json
{
  "_id": "ObjectId",
  "book_id": 1,
  "editions": [
    {
      "format": "hardcover",
      "publisher": "Bloomsbury",
      "year": 1997,
      "isbn": "9780747532743",
      "pages": 223
    },
    {
      "format": "paperback",
      "publisher": "Bloomsbury",
      "year": 2004,
      "isbn": "9780747558194",
      "pages": 250
    }
  ],
  "tags": ["magic-school", "chosen-one", "british", "young-adult"],
  "awards": [
    { "name": "British Book Awards Children's Book of the Year", "year": 1997 },
    { "name": "Nestlé Smarties Book Prize", "year": 1997 }
  ],
  "series": {
    "name": "Harry Potter",
    "position": 1,
    "total": 7
  },
  "reading_level": "9-12 years",
  "created_at": "2026-05-20T00:00:00Z"
}
```

**Indexes:**
- `{ book_id: 1 }` — unique
- `{ tags: 1 }` — search by tag
- `{ "awards.name": 1 }` — find award-winning books

### 2.4 `activity_logs` Collection

Time-series event log for user actions (views, searches, list modifications).

```json
{
  "_id": "ObjectId",
  "user_id": 1,
  "action": "view_book",
  "resource_type": "book",
  "resource_id": 3,
  "details": {
    "from_page": "search_results",
    "search_query": "fantasy epic"
  },
  "ip_address": "192.168.1.1",
  "timestamp": "2026-05-26T15:30:00Z"
}
```

**Indexes:**
- `{ user_id: 1, timestamp: -1 }` — user activity timeline
- `{ timestamp: -1 }` — TTL index (auto-delete after 90 days)
- `{ action: 1, timestamp: -1 }` — aggregate by action type

---

## 3. Modeling Choices: Embedded vs. Referenced

| Relationship | Strategy | Justification |
|-------------|----------|---------------|
| User → Reading Lists | **One-to-few** embedded | A user rarely has >50 lists; embedding avoids JOINs |
| Reading List → Books | **One-to-few** embedded | Books in a list are read together; embedding is optimal |
| Review → Sentiment | **One-to-one** referenced | Sentiment analysis happens asynchronously; separate collection allows independent scaling |
| Book → Metadata | **One-to-one** referenced | Metadata is optional and may be very large; separation keeps the relational `books` table lean |

---

## 4. Consistency Strategy

Since data spans two database systems, we implement **eventual consistency** with application-level coordination:

1. **Write path**: The Flask backend writes to both DBs in sequence (SQL first, then MongoDB).
2. **Read path**: Queries against one DB at a time (no cross-DB JOINs in a single query).
3. **Compensation**: If MongoDB write fails after SQL write succeeds, a background job reconciles or the user is prompted to retry.
