// ============================================================
// BookHive NoSQL Database — MongoDB Seed Data
// INF2003 Group 11
// Usage: mongosh < seed_data.js
//   or:  mongo bookhive < seed_data.js
// ============================================================

// Switch to BookHive database
db = db.getSiblingDB('bookhive');

// Clear existing data (optional — comment out to preserve)
db.reading_lists.drop();
db.review_sentiments.drop();
db.book_metadata.drop();
db.activity_logs.drop();

print('--- Seeding reading_lists ---');

// ============================================================
// READING LISTS
// ============================================================
db.reading_lists.insertMany([
    {
        user_id: 1,
        list_name: "Want to Read",
        description: "Books I'm excited to read this year",
        is_public: true,
        books: [
            {
                book_id: 6,
                title: "The Three-Body Problem",
                isbn: "9780765382030",
                added_at: new Date("2026-03-15T08:00:00Z"),
                notes: "Heard great things about this sci-fi series"
            },
            {
                book_id: 4,
                title: "Murder on the Orient Express",
                isbn: "9780062073488",
                added_at: new Date("2026-04-10T14:30:00Z"),
                notes: "Never read Christie before"
            }
        ],
        created_at: new Date("2026-01-15T08:00:00Z"),
        updated_at: new Date("2026-04-10T14:30:00Z")
    },
    {
        user_id: 1,
        list_name: "Favorites",
        description: "The best books I've ever read",
        is_public: true,
        books: [
            {
                book_id: 1,
                title: "Harry Potter and the Philosopher's Stone",
                isbn: "9780747532743",
                added_at: new Date("2026-01-15T08:05:00Z"),
                notes: "Childhood favorite that started my love for reading"
            }
        ],
        created_at: new Date("2026-01-15T08:05:00Z"),
        updated_at: new Date("2026-01-15T08:05:00Z")
    },
    {
        user_id: 2,
        list_name: "Currently Reading",
        description: "Books I'm actively reading right now",
        is_public: false,
        books: [
            {
                book_id: 2,
                title: "A Game of Thrones",
                isbn: "9780553103540",
                added_at: new Date("2026-05-01T12:00:00Z"),
                notes: "On chapter 32 — the world-building is incredible"
            }
        ],
        created_at: new Date("2026-05-01T12:00:00Z"),
        updated_at: new Date("2026-05-20T18:00:00Z")
    },
    {
        user_id: 2,
        list_name: "Sci-Fi Favorites",
        description: "Top science fiction recommendations",
        is_public: true,
        books: [
            {
                book_id: 6,
                title: "The Three-Body Problem",
                isbn: "9780765382030",
                added_at: new Date("2026-02-20T09:00:00Z"),
                notes: "Mind-blowing hard sci-fi"
            }
        ],
        created_at: new Date("2026-02-20T09:00:00Z"),
        updated_at: new Date("2026-02-20T09:00:00Z")
    },
    {
        user_id: 3,
        list_name: "Teaching Literature",
        description: "Books I use in my university courses",
        is_public: true,
        books: [
            {
                book_id: 5,
                title: "Norwegian Wood",
                isbn: "9780375704024",
                added_at: new Date("2026-01-10T07:00:00Z"),
                notes: "Core text for my Modern Asian Literature module"
            },
            {
                book_id: 3,
                title: "The Lord of the Rings",
                isbn: "9780547928227",
                added_at: new Date("2026-01-10T07:05:00Z"),
                notes: "Used in Fantasy Literature 101"
            }
        ],
        created_at: new Date("2026-01-10T07:00:00Z"),
        updated_at: new Date("2026-05-15T16:00:00Z")
    }
]);

print('--- Seeding review_sentiments ---');

// ============================================================
// REVIEW SENTIMENTS
// ============================================================
db.review_sentiments.insertMany([
    {
        review_id: 1,
        book_id: 1,
        sentiment_score: 0.92,
        sentiment_label: "positive",
        keywords: ["magical", "masterpiece", "timeless", "classic", "world-building"],
        language: "en",
        analyzed_at: new Date("2026-05-21T12:00:00Z")
    },
    {
        review_id: 2,
        book_id: 2,
        sentiment_score: 0.65,
        sentiment_label: "positive",
        keywords: ["epic", "complex", "brilliant", "characters", "learning-curve"],
        language: "en",
        analyzed_at: new Date("2026-05-21T12:05:00Z")
    },
    {
        review_id: 3,
        book_id: 1,
        sentiment_score: 0.88,
        sentiment_label: "positive",
        keywords: ["childhood", "favorite", "magic", "nostalgia"],
        language: "en",
        analyzed_at: new Date("2026-05-21T12:10:00Z")
    },
    {
        review_id: 4,
        book_id: 3,
        sentiment_score: 0.95,
        sentiment_label: "positive",
        keywords: ["masterpiece", "unmatched", "world-building", "linguistic", "creativity"],
        language: "en",
        analyzed_at: new Date("2026-05-21T12:15:00Z")
    },
    {
        review_id: 5,
        book_id: 5,
        sentiment_score: 0.72,
        sentiment_label: "positive",
        keywords: ["melancholic", "loneliness", "love", "beautiful"],
        language: "en",
        analyzed_at: new Date("2026-05-21T12:20:00Z")
    },
    {
        review_id: 6,
        book_id: 6,
        sentiment_score: 0.90,
        sentiment_label: "positive",
        keywords: ["mind-bending", "original", "science-fiction", "brilliant"],
        language: "en",
        analyzed_at: new Date("2026-05-21T12:25:00Z")
    },
    {
        review_id: 7,
        book_id: 7,
        sentiment_score: 0.55,
        sentiment_label: "positive",
        keywords: ["twists", "unreliable-narrator", "suspense", "thriller"],
        language: "en",
        analyzed_at: new Date("2026-05-21T12:30:00Z")
    },
    {
        review_id: 8,
        book_id: 4,
        sentiment_score: 0.94,
        sentiment_label: "positive",
        keywords: ["classic", "whodunit", "stunning", "reveal", "detective"],
        language: "en",
        analyzed_at: new Date("2026-05-21T12:35:00Z")
    },
    {
        review_id: 9,
        book_id: 5,
        sentiment_score: 0.40,
        sentiment_label: "neutral",
        keywords: ["slow", "pacing", "beautiful", "writing"],
        language: "en",
        analyzed_at: new Date("2026-05-21T12:40:00Z")
    },
    {
        review_id: 10,
        book_id: 6,
        sentiment_score: 0.78,
        sentiment_label: "positive",
        keywords: ["hard-sci-fi", "scientific", "payoff", "immense"],
        language: "en",
        analyzed_at: new Date("2026-05-21T12:45:00Z")
    }
]);

print('--- Seeding book_metadata ---');

// ============================================================
// BOOK METADATA
// ============================================================
db.book_metadata.insertMany([
    {
        book_id: 1,
        editions: [
            { format: "hardcover", publisher: "Bloomsbury", year: 1997, isbn: "9780747532743", pages: 223 },
            { format: "paperback", publisher: "Bloomsbury", year: 2004, isbn: "9780747558194", pages: 250 },
            { format: "illustrated", publisher: "Bloomsbury", year: 2015, isbn: "9781408845646", pages: 256 }
        ],
        tags: ["magic-school", "chosen-one", "british", "young-adult", "coming-of-age"],
        awards: [
            { name: "British Book Awards Children's Book of the Year", year: 1997 },
            { name: "Nestlé Smarties Book Prize", year: 1997 }
        ],
        series: { name: "Harry Potter", position: 1, total: 7 },
        reading_level: "9-12 years",
        created_at: new Date("2026-05-20T00:00:00Z")
    },
    {
        book_id: 2,
        editions: [
            { format: "hardcover", publisher: "Bantam Books", year: 1996, isbn: "9780553103540", pages: 694 },
            { format: "paperback", publisher: "Bantam Books", year: 2011, isbn: "9780553593716", pages: 835 }
        ],
        tags: ["epic-fantasy", "political-intrigue", "dragons", "medieval", "dark-fantasy"],
        awards: [
            { name: "Locus Award for Best Fantasy Novel", year: 1997 },
            { name: "Hugo Award Nominee", year: 1997 }
        ],
        series: { name: "A Song of Ice and Fire", position: 1, total: 7 },
        reading_level: "Adult",
        created_at: new Date("2026-05-20T00:00:00Z")
    },
    {
        book_id: 3,
        editions: [
            { format: "hardcover", publisher: "Allen & Unwin", year: 1954, isbn: "9780547928227", pages: 1178 },
            { format: "paperback", publisher: "HarperCollins", year: 2012, isbn: "9780544003415", pages: 1216 }
        ],
        tags: ["high-fantasy", "quest", "classic", "middle-earth", "mythology"],
        awards: [
            { name: "International Fantasy Award", year: 1957 }
        ],
        series: { name: "The Lord of the Rings", position: 1, total: 3 },
        reading_level: "Young Adult+",
        created_at: new Date("2026-05-20T00:00:00Z")
    },
    {
        book_id: 4,
        editions: [
            { format: "hardcover", publisher: "Collins Crime Club", year: 1934, isbn: "9780062073488", pages: 256 }
        ],
        tags: ["detective", "whodunit", "classic-mystery", "locked-room", "hercule-poirot"],
        awards: [],
        series: { name: "Hercule Poirot", position: 10, total: 33 },
        reading_level: "Adult",
        created_at: new Date("2026-05-20T00:00:00Z")
    },
    {
        book_id: 5,
        editions: [
            { format: "hardcover", publisher: "Kodansha", year: 1987, isbn: "9780375704024", pages: 296 },
            { format: "paperback", publisher: "Vintage", year: 2000, isbn: "9780375704024", pages: 296 }
        ],
        tags: ["japanese-literature", "romance", "coming-of-age", "1960s", "music"],
        awards: [],
        series: null,
        reading_level: "Adult",
        created_at: new Date("2026-05-20T00:00:00Z")
    },
    {
        book_id: 6,
        editions: [
            { format: "hardcover", publisher: "Chongqing Press", year: 2008, isbn: "9780765382030", pages: 400 },
            { format: "paperback", publisher: "Tor Books", year: 2014, isbn: "9780765382030", pages: 416 }
        ],
        tags: ["hard-sci-fi", "alien-invasion", "chinese-literature", "physics", "cultural-revolution"],
        awards: [
            { name: "Hugo Award for Best Novel", year: 2015 },
            { name: "Nebula Award Nominee", year: 2014 }
        ],
        series: { name: "Remembrance of Earth's Past", position: 1, total: 3 },
        reading_level: "Adult",
        created_at: new Date("2026-05-20T00:00:00Z")
    },
    {
        book_id: 7,
        editions: [
            { format: "hardcover", publisher: "Crown Publishing", year: 2012, isbn: "9780307588364", pages: 432 }
        ],
        tags: ["psychological-thriller", "unreliable-narrator", "marriage", "twist", "crime"],
        awards: [
            { name: "Goodreads Choice Award for Best Mystery & Thriller", year: 2012 }
        ],
        series: null,
        reading_level: "Adult",
        created_at: new Date("2026-05-20T00:00:00Z")
    }
]);

print('--- Seeding activity_logs ---');

// ============================================================
// ACTIVITY LOGS
// ============================================================
db.activity_logs.insertMany([
    {
        user_id: 1,
        action: "login",
        resource_type: "session",
        resource_id: null,
        details: { browser: "Chrome", os: "Windows" },
        ip_address: "192.168.1.100",
        timestamp: new Date("2026-05-26T08:00:00Z")
    },
    {
        user_id: 1,
        action: "search_books",
        resource_type: "search",
        resource_id: null,
        details: { query: "fantasy", results_count: 3 },
        ip_address: "192.168.1.100",
        timestamp: new Date("2026-05-26T08:05:00Z")
    },
    {
        user_id: 1,
        action: "view_book",
        resource_type: "book",
        resource_id: 1,
        details: { from_page: "search_results" },
        ip_address: "192.168.1.100",
        timestamp: new Date("2026-05-26T08:06:00Z")
    },
    {
        user_id: 2,
        action: "login",
        resource_type: "session",
        resource_id: null,
        details: { browser: "Firefox", os: "Mac" },
        ip_address: "10.0.0.50",
        timestamp: new Date("2026-05-26T09:00:00Z")
    },
    {
        user_id: 2,
        action: "add_to_list",
        resource_type: "reading_list",
        resource_id: null,
        details: { list_name: "Currently Reading", book_id: 2, book_title: "A Game of Thrones" },
        ip_address: "10.0.0.50",
        timestamp: new Date("2026-05-26T09:15:00Z")
    },
    {
        user_id: 3,
        action: "write_review",
        resource_type: "review",
        resource_id: 5,
        details: { book_id: 5, rating: 4 },
        ip_address: "172.16.0.25",
        timestamp: new Date("2026-05-26T10:30:00Z")
    },
    {
        user_id: 4,
        action: "view_book",
        resource_type: "book",
        resource_id: 7,
        details: { from_page: "homepage" },
        ip_address: "192.168.2.75",
        timestamp: new Date("2026-05-26T11:00:00Z")
    },
    {
        user_id: 4,
        action: "create_list",
        resource_type: "reading_list",
        resource_id: null,
        details: { list_name: "Mystery Must-Reads" },
        ip_address: "192.168.2.75",
        timestamp: new Date("2026-05-26T11:05:00Z")
    }
]);

print('');
print('========================================');
print('  MongoDB seeding complete!');
print('  Database: bookhive');
print('  Collections: reading_lists, review_sentiments, book_metadata, activity_logs');
print('========================================');
