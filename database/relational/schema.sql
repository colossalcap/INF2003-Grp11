-- ============================================================
-- BookHive Relational Database Schema
-- INF2003 Group 11
-- Target: SQLite (dev) / MySQL (production)
-- ============================================================

-- Enable foreign key support (SQLite)
PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- Table: users
-- Stores registered user accounts
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username        VARCHAR(50)  NOT NULL UNIQUE,
    email           VARCHAR(100) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    display_name    VARCHAR(100),
    bio             TEXT,
    avatar_url      VARCHAR(255),
    role            VARCHAR(20)  DEFAULT 'reader'  CHECK (role IN ('reader', 'author', 'admin')),
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    last_login      DATETIME
);

-- ------------------------------------------------------------
-- Table: authors
-- Stores book author information
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS authors (
    author_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(100) NOT NULL,
    biography       TEXT,
    birth_date      DATE,
    nationality     VARCHAR(50),
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- Table: categories
-- Stores book genre/category information
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    category_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(50)  NOT NULL UNIQUE,
    description     TEXT,
    parent_category_id INTEGER   REFERENCES categories(category_id)
                                  ON DELETE SET NULL
);

-- ------------------------------------------------------------
-- Table: books
-- Core book catalog
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS books (
    book_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn            VARCHAR(13)  UNIQUE,
    title           VARCHAR(255) NOT NULL,
    publisher       VARCHAR(100),
    publication_year INTEGER,
    page_count      INTEGER      CHECK (page_count > 0),
    language        VARCHAR(30)  DEFAULT 'English',
    description     TEXT,
    cover_url       VARCHAR(255),
    average_rating  DECIMAL(3,2) DEFAULT 0.00 CHECK (average_rating >= 0 AND average_rating <= 5.00),
    rating_count    INTEGER      DEFAULT 0,
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- Junction Table: book_authors (M:M)
-- Links books to their authors
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS book_authors (
    book_id         INTEGER NOT NULL REFERENCES books(book_id)
                                  ON DELETE CASCADE,
    author_id       INTEGER NOT NULL REFERENCES authors(author_id)
                                  ON DELETE CASCADE,
    PRIMARY KEY (book_id, author_id)
);

-- ------------------------------------------------------------
-- Junction Table: book_categories (M:M)
-- Links books to their categories/genres
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS book_categories (
    book_id         INTEGER NOT NULL REFERENCES books(book_id)
                                  ON DELETE CASCADE,
    category_id     INTEGER NOT NULL REFERENCES categories(category_id)
                                  ON DELETE CASCADE,
    PRIMARY KEY (book_id, category_id)
);

-- ------------------------------------------------------------
-- Table: reviews
-- User book reviews with ratings
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reviews (
    review_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(user_id)
                                  ON DELETE CASCADE,
    book_id         INTEGER NOT NULL REFERENCES books(book_id)
                                  ON DELETE CASCADE,
    rating          INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title           VARCHAR(200),
    body            TEXT,
    spoiler_alert   BOOLEAN DEFAULT 0,
    helpful_count   INTEGER DEFAULT 0,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, book_id)  -- one review per user per book
);

-- ------------------------------------------------------------
-- Indexes for performance optimization
-- ------------------------------------------------------------
CREATE INDEX idx_books_title        ON books(title);
CREATE INDEX idx_books_rating       ON books(average_rating);
CREATE INDEX idx_reviews_book       ON reviews(book_id);
CREATE INDEX idx_reviews_user       ON reviews(user_id);
CREATE INDEX idx_reviews_rating     ON reviews(rating);
CREATE INDEX idx_users_email        ON users(email);
CREATE INDEX idx_authors_name       ON authors(name);

-- ------------------------------------------------------------
-- Trigger 1: Auto-update book average rating after review insert
-- Demonstrates advanced SQL: TRIGGER + nested SELECT
-- ------------------------------------------------------------
CREATE TRIGGER IF NOT EXISTS trg_update_book_rating_insert
AFTER INSERT ON reviews
BEGIN
    UPDATE books
    SET average_rating = (
        SELECT ROUND(AVG(CAST(rating AS REAL)), 2)
        FROM reviews
        WHERE book_id = NEW.book_id
    ),
    rating_count = (
        SELECT COUNT(*)
        FROM reviews
        WHERE book_id = NEW.book_id
    )
    WHERE book_id = NEW.book_id;
END;

-- ------------------------------------------------------------
-- Trigger 2: Auto-update book average rating after review update
-- ------------------------------------------------------------
CREATE TRIGGER IF NOT EXISTS trg_update_book_rating_update
AFTER UPDATE OF rating ON reviews
BEGIN
    UPDATE books
    SET average_rating = (
        SELECT ROUND(AVG(CAST(rating AS REAL)), 2)
        FROM reviews
        WHERE book_id = NEW.book_id
    ),
    rating_count = (
        SELECT COUNT(*)
        FROM reviews
        WHERE book_id = NEW.book_id
    )
    WHERE book_id = NEW.book_id;
END;

-- ------------------------------------------------------------
-- Trigger 3: Auto-update book average rating after review delete
-- ------------------------------------------------------------
CREATE TRIGGER IF NOT EXISTS trg_update_book_rating_delete
AFTER DELETE ON reviews
BEGIN
    UPDATE books
    SET average_rating = (
        SELECT ROUND(AVG(CAST(rating AS REAL)), 2)
        FROM reviews
        WHERE book_id = OLD.book_id
    ),
    rating_count = (
        SELECT COUNT(*)
        FROM reviews
        WHERE book_id = OLD.book_id
    )
    WHERE book_id = OLD.book_id;
END;

-- ------------------------------------------------------------
-- Trigger 4: Auto-update reviews.updated_at on modification
-- ------------------------------------------------------------
CREATE TRIGGER IF NOT EXISTS trg_reviews_updated_at
AFTER UPDATE ON reviews
BEGIN
    UPDATE reviews SET updated_at = CURRENT_TIMESTAMP
    WHERE review_id = NEW.review_id;
END;
