-- ============================================================
-- BookHive Relational Database — Seed Data
-- INF2003 Group 11
-- ============================================================

-- Users (passwords are hashed — use 'password123' for testing)
INSERT INTO users (username, email, password_hash, display_name, bio, role) VALUES
('jane_reader',  'jane@example.com',  '$2b$12$LJ3m4ys3GZfnYMz8kVsKaOTSGLkyVlMJ3fSTurNWRfLmRblvOvVRO', 'Jane Doe',    'Avid reader and book collector',          'reader'),
('john_books',   'john@example.com',  '$2b$12$LJ3m4ys3GZfnYMz8kVsKaOTSGLkyVlMJ3fSTurNWRfLmRblvOvVRO', 'John Smith',  'Sci-fi enthusiast and aspiring writer',    'reader'),
('alice_words',  'alice@example.com', '$2b$12$LJ3m4ys3GZfnYMz8kVsKaOTSGLkyVlMJ3fSTurNWRfLmRblvOvVRO', 'Alice Wang',  'Literature professor at NUS',              'author'),
('bob_pages',    'bob@example.com',   '$2b$12$LJ3m4ys3GZfnYMz8kVsKaOTSGLkyVlMJ3fSTurNWRfLmRblvOvVRO', 'Bob Tan',     'Mystery and thriller fan',                 'reader'),
('admin_hive',   'admin@bookhive.com','$2b$12$LJ3m4ys3GZfnYMz8kVsKaOTSGLkyVlMJ3fSTurNWRfLmRblvOvVRO', 'Admin',       'BookHive system administrator',            'admin');

-- Authors
INSERT INTO authors (name, biography, birth_date, nationality) VALUES
('J.K. Rowling',       'British author best known for the Harry Potter series.',                  '1965-07-31', 'British'),
('George R.R. Martin', 'American novelist and short story writer, author of A Song of Ice and Fire.', '1948-09-20', 'American'),
('J.R.R. Tolkien',     'English writer, poet, and philologist, author of The Lord of the Rings.',  '1892-01-03', 'British'),
('Agatha Christie',    'English writer known for her 66 detective novels.',                        '1890-09-15', 'British'),
('Haruki Murakami',    'Japanese writer known for surrealistic and melancholic narratives.',       '1949-01-12', 'Japanese'),
('Liu Cixin',          'Chinese science fiction writer, author of The Three-Body Problem.',       '1963-06-23', 'Chinese'),
('Gillian Flynn',      'American author known for psychological thrillers like Gone Girl.',       '1971-02-24', 'American');

-- Categories
INSERT INTO categories (name, description, parent_category_id) VALUES
('Fiction',           'Works of imaginative narration',                              NULL),
('Non-Fiction',       'Factual and informative works',                                NULL),
('Science Fiction',   'Fiction based on imagined future scientific advances',         1),
('Fantasy',           'Fiction involving magic and supernatural elements',            1),
('Mystery',           'Fiction dealing with the solution of a crime or puzzle',       1),
('Thriller',          'Fiction characterized by fast-paced, suspenseful plots',       1),
('Literary Fiction',  'Fiction with artistic and intellectual merit',                 1),
('Biography',         'An account of someone''s life written by another',             2),
('History',           'Study of past events',                                         2),
('Science',           'Systematic study of the physical and natural world',           2);

-- Books
INSERT INTO books (isbn, title, publisher, publication_year, page_count, language, description) VALUES
('9780747532743', 'Harry Potter and the Philosopher''s Stone', 'Bloomsbury',         1997, 223,  'English', 'The first novel in the Harry Potter series.'),
('9780553103540', 'A Game of Thrones',                        'Bantam Books',        1996, 694,  'English', 'The first book in A Song of Ice and Fire.'),
('9780547928227', 'The Lord of the Rings',                    'Allen & Unwin',       1954, 1178, 'English', 'Epic high-fantasy novel set in Middle-earth.'),
('9780062073488', 'Murder on the Orient Express',             'Collins Crime Club',  1934, 256,  'English', 'Hercule Poirot solves a murder on a luxury train.'),
('9780375704024', 'Norwegian Wood',                           'Kodansha',            1987, 296,  'Japanese', 'A nostalgic story of love and loss in 1960s Tokyo.'),
('9780765382030', 'The Three-Body Problem',                   'Chongqing Press',     2008, 400,  'Chinese', 'Aliens threaten to invade Earth in this hard sci-fi novel.'),
('9780307588364', 'Gone Girl',                                'Crown Publishing',    2012, 432,  'English', 'A psychological thriller about a wife''s disappearance.');

-- Book-Author links (M:M)
INSERT INTO book_authors (book_id, author_id) VALUES
(1, 1),                     -- Harry Potter → J.K. Rowling
(2, 2),                     -- Game of Thrones → George R.R. Martin
(3, 3),                     -- LOTR → J.R.R. Tolkien
(4, 4),                     -- Murder on Orient Express → Agatha Christie
(5, 5),                     -- Norwegian Wood → Haruki Murakami
(6, 6),                     -- Three-Body Problem → Liu Cixin
(7, 7);                     -- Gone Girl → Gillian Flynn

-- Book-Category links (M:M)
INSERT INTO book_categories (book_id, category_id) VALUES
(1, 4),  -- Harry Potter → Fantasy
(1, 1),  -- Harry Potter → Fiction
(2, 4),  -- Game of Thrones → Fantasy
(2, 1),  -- Game of Thrones → Fiction
(3, 4),  -- LOTR → Fantasy
(3, 1),  -- LOTR → Fiction
(4, 5),  -- Murder on Orient Express → Mystery
(4, 1),  -- Murder on Orient Express → Fiction
(5, 7),  -- Norwegian Wood → Literary Fiction
(5, 1),  -- Norwegian Wood → Fiction
(6, 3),  -- Three-Body Problem → Science Fiction
(6, 1),  -- Three-Body Problem → Fiction
(7, 6),  -- Gone Girl → Thriller
(7, 5),  -- Gone Girl → Mystery
(7, 1);  -- Gone Girl → Fiction

-- Reviews
INSERT INTO reviews (user_id, book_id, rating, title, body, spoiler_alert) VALUES
(1, 1, 5, 'Magical masterpiece!',           'Harry Potter is a timeless classic that captivates readers of all ages. The world-building is extraordinary.', 0),
(1, 2, 4, 'Epic but complex',               'A Game of Thrones is brilliantly written but has a steep learning curve with its many characters.',             0),
(2, 1, 5, 'Childhood favorite',             'I grew up reading this. The magic never fades.',                                                                  0),
(2, 3, 5, 'The ultimate fantasy',           'Tolkien''s masterpiece. Unmatched world-building and linguistic creativity.',                                     0),
(3, 5, 4, 'Beautifully melancholic',        'Murakami captures the essence of loneliness and love in a way few authors can.',                                0),
(3, 6, 5, 'Mind-bending sci-fi',            'The Three-Body Problem is one of the most original science fiction novels I''ve ever read.',                    0),
(4, 7, 4, 'Twists and turns!',              'Gillian Flynn keeps you guessing until the very last page. A masterclass in unreliable narration.',             1),
(4, 4, 5, 'Classic whodunit',               'Agatha Christie at her finest. The final reveal is absolutely stunning.',                                       0),
(1, 5, 3, 'Not my favorite Murakami',       'While beautifully written, the pacing felt slow at times compared to his other works.',                         0),
(2, 6, 4, 'Hard sci-fi at its best',        'Requires some scientific background knowledge, but the payoff is immense.',                                     0);
