# G11 — Progress Report (Template)
## INF2003 Group Project — BookHive

> **Note:** This is a template. Fill in your team's details and progress.
> Max 4 pages (excluding cover page). Submit as `G11_Progress Report.pdf`.

---

## Cover Page

| Field | Detail |
|-------|--------|
| **Module** | INF2003 Database Design & Implementation |
| **Group ID** | G11 |
| **Project Title** | BookHive: Book Review & Community Platform |
| **Team Members** | [Name 1], [Name 2], [Name 3], [Name 4] |
| **Team Lead** | [Name] ([email]) |
| **Submission Date** | June 22, 2026 |

---

## 1. Application Background & Problem Statement

### 1.1 Background
BookHive is a web-based book discovery and review platform designed to help readers find their next great read. In an age of information overload, readers face difficulty discovering quality books that match their personal tastes. Existing platforms like Goodreads offer basic functionality but lack the flexible data model needed for modern book metadata (multiple editions, dynamic tagging, AI-driven sentiment analysis).

### 1.2 Problem Statement
- Readers need a centralized platform to track reading progress, write reviews, and discover new books.
- Traditional relational databases alone struggle with sparse, heterogeneous book metadata (awards, editions, translations).
- Reading lists are inherently user-defined and benefit from a flexible schema.
- Review sentiment trends provide valuable insights that are better modeled in a document database.

### 1.3 Objectives
1. Design a normalized relational database (≥5 tables) with various relationship types
2. Implement a NoSQL document database for flexible metadata and reading lists
3. Build a functional web application with CRUD operations on both databases
4. Demonstrate complex SQL queries (nested queries, triggers, aggregations)
5. Demonstrate MongoDB aggregation pipelines and complex queries
6. Provide a user-friendly interface for browsing books and managing reviews

---

## 2. System Architecture

```
┌─────────────────────────────────────────┐
│          Presentation Layer              │
│     HTML5 / Bootstrap 5 / JavaScript     │
│          (Jinja2 Templates)              │
└──────────────────┬──────────────────────┘
                   │ HTTP/REST
┌──────────────────▼──────────────────────┐
│          Application Layer               │
│        Flask (Python 3.10+)              │
│     SQLAlchemy ORM + PyMongo             │
└─────┬────────────────────────┬──────────┘
      │                        │
┌─────▼────────┐    ┌──────────▼──────────┐
│  Relational   │    │     NoSQL           │
│  SQLite/MySQL │    │   MongoDB           │
│               │    │                     │
│  5 tables +   │    │  4 collections:     │
│  2 junctions  │    │  • reading_lists    │
│  4 triggers   │    │  • review_sentiments│
│               │    │  • book_metadata    │
│               │    │  • activity_logs    │
└──────────────┘    └─────────────────────┘
```

---

## 3. Dataset Description

### 3.1 Data Sources
| Source | Description | Records |
|--------|-------------|---------|
| Kaggle: Goodreads Books Dataset | Book metadata, ratings, authors | ~10,000 books (subset used) |
| Custom-generated | User accounts, reviews, reading lists | Synthetic but realistic |
| data.gov.sg (optional) | Library circulation data for Singapore context | TBD |

### 3.2 Data Characteristics
- **Books**: ISBN, title, publisher, year, page count, language
- **Authors**: Name, nationality, biography (up to 7 sample authors, expandable)
- **Categories**: Hierarchical genre system (10 categories with parent-child relationships)
- **Reviews**: User-generated ratings (1-5), review text, timestamps
- **Users**: Registration data with role-based access (reader/author/admin)

---

## 4. Planned Functionalities

### 4.1 Core Features (All CRUD)
| Feature | Relational | NoSQL |
|---------|-----------|-------|
| User Registration/Login | `users` table (INSERT, SELECT) | `activity_logs` (log logins) |
| Browse Books | `books` + JOINs (SELECT) | `book_metadata` (tags, editions) |
| Write Reviews | `reviews` (INSERT, UPDATE, DELETE) | `review_sentiments` (INSERT) |
| Manage Reading Lists | — | `reading_lists` (full CRUD) |
| Search | `books` with LIKE/WHERE | `book_metadata` text search |
| View Dashboard | Aggregation queries | Aggregation pipelines |

### 4.2 Advanced Features
- **Triggers**: Auto-update `books.average_rating` on review changes (3 triggers)
- **Nested Queries**: Find users who rated above average, books with no reviews
- **MongoDB Aggregation**: Sentiment analysis by book, popular keywords, user reading stats
- **Cross-DB Consistency**: Application-level coordination between SQL and MongoDB writes

---

## 5. Implementation Progress (as of Jun 22)

| Component | Status | Notes |
|-----------|--------|-------|
| Database Schema Design | ✅ Complete | 7 tables + 4 collections designed |
| ER Diagram | ✅ Complete | Documented in `docs/ER_Diagram.md` |
| SQL DDL (schema.sql) | ✅ Complete | Tables, indexes, triggers defined |
| Seed Data (SQL) | ✅ Complete | 5 users, 7 authors, 10 categories, 7 books, 10 reviews |
| NoSQL Schema Design | ✅ Complete | Rationale documented in `schema_design.md` |
| MongoDB Seed Data | ✅ Complete | 4 collections with realistic sample data |
| SQL Queries | ✅ Complete | CRUD + nested + aggregation + UNION queries |
| MongoDB Queries | ✅ Complete | CRUD + aggregation pipelines + $lookup |
| Flask Backend (models) | 🔄 In Progress | SQLAlchemy models defined |
| Flask Backend (routes) | 🔄 In Progress | Auth and book routes being implemented |
| Frontend (templates) | 🔄 In Progress | Base layout and homepage created |
| Web Application Integration | ⬜ Not Started | — |

---

## 6. Timeline (Gantt Overview)

```
Week 1-2 (May 26 - Jun 8):   Schema design, ERD, dataset selection
Week 3-4 (Jun 9 - Jun 22):   Backend implementation, Progress Report  ← WE ARE HERE
Week 5-6 (Jun 23 - Jul 6):   Frontend, integration, testing
Week 7   (Jul 7 - Jul 13):   Final report, slides, video recording
Week 8   (Jul 14 - Jul 17):  Peer review submission
```

---

*End of Progress Report*
