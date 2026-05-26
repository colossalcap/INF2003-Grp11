# G11 — Final Report (Template)
## INF2003 Group Project — BookHive

> **Note:** This is a template. Expand with your team's actual results.
> Max 8 pages (excluding cover page and appendix). Submit as `G11_Final Report.PDF`.

---

## Cover Page

| Field | Detail |
|-------|--------|
| **Module** | INF2003 Database Design & Implementation |
| **Group ID** | G11 |
| **Project Title** | BookHive: Book Review & Community Platform |
| **Team Members** | [Name 1], [Name 2], [Name 3], [Name 4] |
| **Team Lead** | [Name] ([email]) |
| **Submission Date** | July 13, 2026 |

---

## 1. Introduction

[Briefly restate the problem, objectives, and scope of BookHive. Summarize what was achieved.]

---

## 2. System-Level Database Integration

### 2.1 Architecture Overview
Describe how the Flask application communicates with both SQLite/MySQL and MongoDB simultaneously. Include the architecture diagram.

### 2.2 Data Flow
Explain the write path (SQL first, then MongoDB) and read path (queries targeted to appropriate DB).

### 2.3 Consistency Strategy
Discuss the eventual consistency model and how application-level coordination handles partial failures.

---

## 3. Relational Database Implementation

### 3.1 Schema Design
Present the final ER diagram. List all tables with their columns, data types, and constraints.

### 3.2 Table Summary

| Table | Rows (sample) | Purpose |
|-------|---------------|---------|
| `users` | 5 | User accounts with role-based access |
| `authors` | 7 | Author biographical data |
| `categories` | 10 | Hierarchical book genres |
| `books` | 7 | Core book catalog |
| `reviews` | 10 | User-generated ratings and reviews |
| `book_authors` | 7 | M:M junction table |
| `book_categories` | 15 | M:M junction table |

### 3.3 Basic CRUD Operations
Provide code snippets and screenshots of:
- Creating a new user
- Reading book details with author/category JOINs
- Updating review content
- Deleting a user (cascade to reviews)

### 3.4 Advanced SQL Features
- **Nested Queries**: Find users who rated above average (show query + output)
- **Aggregation with HAVING**: Categories with avg rating > 4.0
- **Correlated Subquery**: Users who reviewed all Fantasy books
- **Triggers**: Demonstrate auto-update of `average_rating` on review INSERT/UPDATE/DELETE
- **UNION**: Combined top-rated and most-reviewed lists

---

## 4. NoSQL Database Implementation

### 4.1 Schema Design & Justification
Reiterate the modeling choices from `schema_design.md`:
- Why embedded documents for reading lists
- Why referenced documents for book metadata
- Why a separate `activity_logs` collection

### 4.2 Collection Summary

| Collection | Documents (sample) | Purpose |
|------------|---------------------|---------|
| `reading_lists` | 5 | Per-user book shelving |
| `review_sentiments` | 10 | NLP sentiment analysis |
| `book_metadata` | 7 | Flexible book metadata |
| `activity_logs` | 8 | High-volume event logging |

### 4.3 Basic CRUD Operations
Provide screenshots/code of:
- Creating a reading list
- Adding books to a list ($push)
- Querying book metadata by tag
- Updating sentiment scores
- Deleting a reading list

### 4.4 Advanced MongoDB Queries
- **Aggregation Pipeline**: Average sentiment per book with 2+ reviews
- **$unwind + $group**: Most common positive keywords
- **$lookup**: Reading lists enriched with sentiment data
- **Text Search**: Full-text search on book tags
- **Bulk Write**: Efficient batch operations

---

## 5. Application Implementation

### 5.1 Web Interface
Screenshots (up to 10) of:
1. Homepage with book listings
2. User registration form
3. Login page
4. Book detail page (with reviews)
5. Write/edit review form
6. Reading list management
7. User dashboard with stats
8. Search results
9. Admin panel (if implemented)
10. Mobile responsive view

### 5.2 Key Frontend Features
- Bootstrap 5 responsive design
- Jinja2 templating for server-side rendering
- JavaScript for dynamic interactions (AJAX review submission)
- Flash messages for user feedback

---

## 6. Performance Evaluation (Optional Enhancement)

Discuss any performance analysis conducted:
- Query execution time comparison (SQL vs MongoDB for similar operations)
- Index impact on search performance
- Memory usage comparison
- Scalability considerations

---

## 7. Constraints & Limitations

- SQLite's limited concurrency support (single-writer)
- MongoDB's eventual consistency may cause stale reads
- No real-time synchronization between SQL and MongoDB
- Small sample dataset limits performance testing validity
- No OAuth/social login implementation

---

## 8. Discussion & Reflections

### 8.1 What Worked Well
- Clear separation of concerns: structured data in SQL, flexible data in MongoDB
- Triggers simplified application logic for rating calculations
- MongoDB aggregation pipelines provided powerful analytics with less code than equivalent SQL

### 8.2 Challenges Faced
- Maintaining consistency across two database systems
- Learning curve for MongoDB query syntax
- Debugging cross-database transactions

### 8.3 Lessons Learned
- Relational databases excel at enforcing data integrity
- NoSQL databases excel at flexible schemas and horizontal scaling
- The right tool depends on the data model, not personal preference

### 8.4 Future Improvements
- Implement database-level transactions with two-phase commit
- Add Redis caching layer for frequently accessed data
- Implement real-time updates via WebSockets
- Deploy to cloud (AWS RDS + MongoDB Atlas)

---

## Appendix (not counted in page limit)

- Full SQL schema code
- Full MongoDB query reference
- Additional screenshots

---

*End of Final Report*
