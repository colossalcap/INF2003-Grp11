# INF2003 Group 11 — BookHive: Book Review & Community Platform

## Team Members

| Name | Email | Role |
|------|-------|------|
| [Member 1] | [email] | [Role] |
| [Member 2] | [email] | [Role] |
| [Member 3] | [email] | [Role] |
| [Member 4] | [email] | Team Lead |

## Project Overview

**BookHive** is a full-stack database application that allows users to discover books, write reviews, create reading lists, and connect with other readers. The platform demonstrates the complementary use of both relational (SQL) and non-relational (NoSQL) database systems.

### Key Features
- User registration & authentication (with login)
- Browse & search books by category, author, rating
- Write, edit, and delete book reviews
- Create and manage personal reading lists
- View reading statistics and community trends
- Flexible book metadata via NoSQL (genres, tags, editions)

## System Architecture

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│         HTML5 / CSS3 / JavaScript                │
│            (Jinja2 Templates)                    │
└─────────────────────┬───────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────┐
│                Backend (Flask)                    │
│              Python 3.10+ REST API               │
└──────────┬──────────────────────┬───────────────┘
           │                      │
┌──────────▼──────────┐  ┌────────▼───────────────┐
│   Relational DB      │  │     NoSQL DB            │
│   (SQLite/MySQL)     │  │   (MongoDB)             │
│                      │  │                         │
│  • Users             │  │  • Reading Lists        │
│  • Books             │  │  • Review Sentiments    │
│  • Authors           │  │  • Book Metadata        │
│  • Categories        │  │  • User Activity Logs   │
│  • Reviews           │  │                         │
└─────────────────────┘  └─────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript |
| Backend | Python 3, Flask |
| Relational DB | SQLite (dev) / MySQL (prod) |
| NoSQL DB | MongoDB (PyMongo) |
| ORM | SQLAlchemy |

## Project Structure

```
INF2003-Grp11/
├── README.md
├── .gitignore
├── docs/
│   ├── G11_Progress_Report.md
│   ├── G11_Final_Report.md
│   └── ER_Diagram.md
├── database/
│   ├── relational/
│   │   ├── schema.sql          # DDL — table creation
│   │   ├── seed_data.sql       # Sample data
│   │   └── queries.sql         # CRUD + complex queries
│   └── nosql/
│       ├── schema_design.md    # NoSQL design rationale
│       ├── seed_data.js        # MongoDB seed script
│       └── queries.js          # MongoDB CRUD operations
├── backend/
│   ├── app.py                  # Flask entry point
│   ├── config.py               # Database configuration
│   ├── requirements.txt
│   ├── models/
│   │   ├── relational.py       # SQLAlchemy models
│   │   └── nosql.py            # MongoDB models/helpers
│   └── routes/
│       ├── auth.py             # Login/register routes
│       ├── books.py            # Book CRUD routes
│       ├── reviews.py          # Review routes
│       └── reading_lists.py    # Reading list (NoSQL) routes
├── frontend/
│   ├── templates/
│   │   ├── base.html           # Base layout
│   │   ├── index.html          # Homepage
│   │   ├── login.html          # Login page
│   │   ├── register.html       # Registration
│   │   ├── dashboard.html      # User dashboard
│   │   ├── books.html          # Book listing
│   │   └── book_detail.html    # Single book view
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
└── screenshots/
    └── (up to 10 screenshots)
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- MongoDB 6.0+ (or MongoDB Atlas)
- pip (Python package manager)

### Installation

```bash
# 1. Clone / navigate to project
cd INF2003-Grp11

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Set up relational database
python -c "from backend.app import db; db.create_all()"

# 5. Seed relational data
sqlite3 database/bookhive.db < database/relational/seed_data.sql

# 6. Seed MongoDB data
mongosh < database/nosql/seed_data.js

# 7. Run the application
python backend/app.py
```

Visit `http://localhost:5000` in your browser.

## Database Design

### Relational Schema (5 tables)

| Table | Description | Key Relationships |
|-------|-------------|-------------------|
| `users` | User accounts | 1→M with reviews, 1→M with reading_lists |
| `authors` | Book authors | M→M with books (via book_authors) |
| `categories` | Book categories/genres | M→M with books (via book_categories) |
| `books` | Book catalog | M→M with authors & categories, 1→M with reviews |
| `reviews` | User book reviews | M→1 with users, M→1 with books |

**Junction tables:** `book_authors`, `book_categories` (for M→M relationships)

### NoSQL Schema (MongoDB)

| Collection | Document Structure | Purpose |
|------------|-------------------|---------|
| `reading_lists` | `{ user_id, list_name, books: [...], created_at }` | Flexible per-user reading lists |
| `review_sentiments` | `{ review_id, sentiment_score, keywords: [...], language }` | NLP sentiment analysis results |
| `book_metadata` | `{ book_id, editions: [...], tags: [...], awards: [...] }` | Dynamic, schema-flexible metadata |
| `activity_logs` | `{ user_id, action, timestamp, details: {...} }` | High-volume event logging |

## Grading Breakdown

| Component | Weight |
|-----------|--------|
| Database Implementation | 40% |
| Application Design/Implementation | 20% |
| Presentation (Slides & Video) | 15% |
| Final Report | 15% |
| Progress Report | 10% |

## Deliverables

| Deadline | Item |
|----------|------|
| Mon, Jun 22, 2026 | Progress Report (G11_Progress Report.pdf) |
| Mon, Jul 13, 2026 | Slides, Video, Final Report, Source Code |
| Fri, Jul 17, 2026 | Peer Review & Supplementary Files |
