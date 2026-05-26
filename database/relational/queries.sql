-- ============================================================
-- BookHive Relational Database — CRUD & Complex Queries
-- INF2003 Group 11
-- ============================================================

-- ============================================================
-- BASIC CRUD OPERATIONS
-- ============================================================

-- CREATE: Register a new user
INSERT INTO users (username, email, password_hash, display_name, role)
VALUES ('new_user', 'new@example.com', '<hashed_password>', 'New Reader', 'reader');

-- READ: Get all books with their average rating
SELECT b.book_id, b.title, b.average_rating, b.rating_count
FROM books b
ORDER BY b.average_rating DESC;

-- READ: Get a single book with author and category details
SELECT b.*, GROUP_CONCAT(DISTINCT a.name) AS authors, GROUP_CONCAT(DISTINCT c.name) AS categories
FROM books b
LEFT JOIN book_authors ba ON b.book_id = ba.book_id
LEFT JOIN authors a ON ba.author_id = a.author_id
LEFT JOIN book_categories bc ON b.book_id = bc.book_id
LEFT JOIN categories c ON bc.category_id = c.category_id
WHERE b.book_id = 1
GROUP BY b.book_id;

-- UPDATE: Update user bio
UPDATE users SET bio = 'Updated biography text.' WHERE user_id = 1;

-- UPDATE: Modify a review
UPDATE reviews
SET rating = 4, body = 'Updated review body.', updated_at = CURRENT_TIMESTAMP
WHERE review_id = 1;

-- DELETE: Remove a review
DELETE FROM reviews WHERE review_id = 10;

-- DELETE: Remove a user account (cascades to reviews)
DELETE FROM users WHERE user_id = 5;

-- ============================================================
-- ADVANCED / COMPLEX QUERIES
-- ============================================================

-- NESTED QUERY: Find users who have rated books above the overall average rating
SELECT DISTINCT u.username, u.display_name
FROM users u
JOIN reviews r ON u.user_id = r.user_id
WHERE r.rating > (
    SELECT AVG(CAST(rating AS REAL)) FROM reviews
)
ORDER BY u.username;

-- NESTED QUERY with NOT EXISTS: Books that have NO reviews yet
SELECT b.title, b.isbn
FROM books b
WHERE NOT EXISTS (
    SELECT 1 FROM reviews r WHERE r.book_id = b.book_id
);

-- AGGREGATION + HAVING: Categories with average book rating above 4.0
SELECT c.name AS category_name,
       COUNT(DISTINCT bc.book_id) AS book_count,
       ROUND(AVG(b.average_rating), 2) AS avg_category_rating
FROM categories c
JOIN book_categories bc ON c.category_id = bc.category_id
JOIN books b ON bc.book_id = b.book_id
GROUP BY c.category_id, c.name
HAVING AVG(b.average_rating) >= 4.0
ORDER BY avg_category_rating DESC;

-- MULTI-JOIN: Full book details with authors, categories, and review count
SELECT b.title,
       GROUP_CONCAT(DISTINCT a.name) AS authors,
       GROUP_CONCAT(DISTINCT c.name) AS genres,
       b.average_rating,
       COUNT(DISTINCT r.review_id) AS review_count,
       b.publication_year
FROM books b
LEFT JOIN book_authors ba ON b.book_id = ba.book_id
LEFT JOIN authors a ON ba.author_id = a.author_id
LEFT JOIN book_categories bc ON b.book_id = bc.book_id
LEFT JOIN categories c ON bc.category_id = c.category_id
LEFT JOIN reviews r ON b.book_id = r.book_id
GROUP BY b.book_id
ORDER BY b.average_rating DESC;

-- CORRELATED SUBQUERY: Find users who have reviewed every book in the 'Fantasy' category
SELECT u.username, u.display_name
FROM users u
WHERE NOT EXISTS (
    -- Fantasy books that this user has NOT reviewed
    SELECT bc.book_id
    FROM book_categories bc
    JOIN categories c ON bc.category_id = c.category_id
    WHERE c.name = 'Fantasy'
    AND bc.book_id NOT IN (
        SELECT r.book_id FROM reviews r WHERE r.user_id = u.user_id
    )
);

-- WINDOW FUNCTION (if MySQL 8+ / PostgreSQL): Rank books by rating within each category
-- (SQLite compatible alternative using subquery)
SELECT b.title,
       c.name AS category,
       b.average_rating,
       (
           SELECT COUNT(*) + 1
           FROM books b2
           JOIN book_categories bc2 ON b2.book_id = bc2.book_id
           WHERE bc2.category_id = bc.category_id
           AND b2.average_rating > b.average_rating
       ) AS rank_in_category
FROM books b
JOIN book_categories bc ON b.book_id = bc.book_id
JOIN categories c ON bc.category_id = c.category_id
ORDER BY c.name, b.average_rating DESC;

-- UNION: Combined list of top-rated books (4.5+) and most-reviewed books (2+ reviews)
SELECT b.title, 'Top Rated' AS list_type, b.average_rating AS score
FROM books b
WHERE b.average_rating >= 4.5
UNION
SELECT b.title, 'Most Reviewed' AS list_type, b.rating_count AS score
FROM books b
WHERE b.rating_count >= 2
ORDER BY list_type, score DESC;

-- TRANSACTION example: Atomic book + author + category insertion
-- BEGIN TRANSACTION;
-- INSERT INTO books (isbn, title, publisher, publication_year) VALUES (...);
-- INSERT INTO book_authors (book_id, author_id) VALUES (...);
-- INSERT INTO book_categories (book_id, category_id) VALUES (...);
-- COMMIT;

-- Stored Procedure equivalent (multi-step query):
-- Find the most active reviewer and their review statistics
SELECT u.display_name,
       u.username,
       COUNT(r.review_id) AS total_reviews,
       ROUND(AVG(CAST(r.rating AS REAL)), 2) AS avg_rating_given,
       MAX(r.created_at) AS last_review_date
FROM users u
JOIN reviews r ON u.user_id = r.user_id
GROUP BY u.user_id
ORDER BY total_reviews DESC
LIMIT 1;
