// ============================================================
// BookHive NoSQL Database — MongoDB CRUD & Complex Queries
// INF2003 Group 11
// ============================================================

// ============================================================
// BASIC CRUD OPERATIONS — reading_lists
// ============================================================

// CREATE: Add a new reading list for a user
db.reading_lists.insertOne({
    user_id: 1,
    list_name: "Book Club Picks",
    description: "Books selected for our monthly book club",
    is_public: true,
    books: [],
    created_at: new Date(),
    updated_at: new Date()
});

// READ: Get all public reading lists for a user
db.reading_lists.find(
    { user_id: 1, is_public: true },
    { list_name: 1, description: 1, "books.title": 1, _id: 0 }
).sort({ updated_at: -1 });

// READ: Get a specific reading list with all book details
db.reading_lists.findOne(
    { user_id: 1, list_name: "Want to Read" }
);

// UPDATE: Add a book to an existing reading list
db.reading_lists.updateOne(
    { user_id: 1, list_name: "Want to Read" },
    {
        $push: {
            books: {
                book_id: 7,
                title: "Gone Girl",
                isbn: "9780307588364",
                added_at: new Date(),
                notes: "Everyone's talking about this one"
            }
        },
        $set: { updated_at: new Date() }
    }
);

// UPDATE: Change list visibility
db.reading_lists.updateOne(
    { user_id: 2, list_name: "Currently Reading" },
    { $set: { is_public: true } }
);

// DELETE: Remove a book from a reading list
db.reading_lists.updateOne(
    { user_id: 1, list_name: "Want to Read" },
    { $pull: { books: { book_id: 7 } } }
);

// DELETE: Remove an entire reading list
db.reading_lists.deleteOne(
    { user_id: 1, list_name: "Book Club Picks" }
);

// ============================================================
// BASIC CRUD OPERATIONS — book_metadata
// ============================================================

// CREATE: Add metadata for a new book
db.book_metadata.insertOne({
    book_id: 8,
    editions: [
        { format: "paperback", publisher: "Test Publisher", year: 2026, pages: 300 }
    ],
    tags: ["sample", "test"],
    awards: [],
    series: null,
    created_at: new Date()
});

// READ: Get all metadata for a book
db.book_metadata.findOne({ book_id: 1 });

// UPDATE: Add a new edition to a book
db.book_metadata.updateOne(
    { book_id: 1 },
    {
        $push: {
            editions: {
                format: "ebook",
                publisher: "Pottermore",
                year: 2012,
                isbn: "9781781100486",
                pages: 345
            }
        }
    }
);

// DELETE: Remove book metadata
db.book_metadata.deleteOne({ book_id: 8 });

// ============================================================
// BASIC CRUD OPERATIONS — review_sentiments
// ============================================================

// CREATE: Add sentiment analysis for a review
db.review_sentiments.insertOne({
    review_id: 11,
    book_id: 3,
    sentiment_score: 0.75,
    sentiment_label: "positive",
    keywords: ["epic", "detailed", "immersive"],
    language: "en",
    analyzed_at: new Date()
});

// READ: Get sentiment for a specific review
db.review_sentiments.findOne({ review_id: 1 });

// UPDATE: Re-analyze a review's sentiment
db.review_sentiments.updateOne(
    { review_id: 1 },
    {
        $set: {
            sentiment_score: 0.94,
            keywords: ["magical", "masterpiece", "timeless", "classic", "extraordinary"]
        }
    }
);

// ============================================================
// ADVANCED / COMPLEX QUERIES
// ============================================================

// AGGREGATION: Average sentiment score per book (pipeline)
db.review_sentiments.aggregate([
    {
        $group: {
            _id: "$book_id",
            avg_sentiment: { $avg: "$sentiment_score" },
            review_count: { $sum: 1 },
            sentiments: { $push: "$sentiment_label" }
        }
    },
    {
        $match: {
            review_count: { $gte: 2 }  // Only books with 2+ analyzed reviews
        }
    },
    { $sort: { avg_sentiment: -1 } }
]);

// AGGREGATION: Most common positive keywords across all reviews
db.review_sentiments.aggregate([
    { $match: { sentiment_label: "positive" } },
    { $unwind: "$keywords" },
    {
        $group: {
            _id: "$keywords",
            count: { $sum: 1 }
        }
    },
    { $sort: { count: -1 } },
    { $limit: 10 }
]);

// FIND with nested field: All reading lists containing a specific book
db.reading_lists.find(
    { "books.book_id": 1 },
    { user_id: 1, list_name: 1, "books.$": 1 }
);

// AGGREGATION: User reading statistics — books per list per user
db.reading_lists.aggregate([
    { $unwind: "$books" },
    {
        $group: {
            _id: "$user_id",
            total_books_listed: { $sum: 1 },
            unique_books: { $addToSet: "$books.book_id" },
            lists_used: { $addToSet: "$list_name" }
        }
    },
    {
        $project: {
            _id: 0,
            user_id: "$_id",
            total_books_listed: 1,
            unique_book_count: { $size: "$unique_books" },
            list_count: { $size: "$lists_used" }
        }
    },
    { $sort: { total_books_listed: -1 } }
]);

// TEXT SEARCH (requires text index): Search book metadata by tags
// db.book_metadata.createIndex({ tags: "text", "series.name": "text" });
db.book_metadata.find(
    { $text: { $search: "fantasy detective" } },
    { score: { $meta: "textScore" }, book_id: 1, tags: 1 }
).sort({ score: { $meta: "textScore" } });

// AGGREGATION: Award-winning books (from metadata) sorted by award count
db.book_metadata.aggregate([
    {
        $project: {
            book_id: 1,
            award_count: { $size: { $ifNull: ["$awards", []] } },
            award_names: "$awards.name"
        }
    },
    { $match: { award_count: { $gt: 0 } } },
    { $sort: { award_count: -1 } }
]);

// AGGREGATION: Activity logs — most common actions in the last 7 days
db.activity_logs.aggregate([
    {
        $match: {
            timestamp: {
                $gte: new Date(new Date() - 7 * 24 * 60 * 60 * 1000)
            }
        }
    },
    {
        $group: {
            _id: "$action",
            count: { $sum: 1 },
            unique_users: { $addToSet: "$user_id" }
        }
    },
    {
        $project: {
            action: "$_id",
            count: 1,
            unique_user_count: { $size: "$unique_users" }
        }
    },
    { $sort: { count: -1 } }
]);

// AGGREGATION with LOOKUP-like pattern: Find reading lists with books
// that have positive sentiment (> 0.7 average)
db.reading_lists.aggregate([
    { $unwind: "$books" },
    {
        $lookup: {
            from: "review_sentiments",
            localField: "books.book_id",
            foreignField: "book_id",
            as: "sentiments"
        }
    },
    { $unwind: { path: "$sentiments", preserveNullAndEmptyArrays: true } },
    {
        $group: {
            _id: {
                user_id: "$user_id",
                list_name: "$list_name",
                book_id: "$books.book_id",
                book_title: "$books.title"
            },
            avg_sentiment: { $avg: "$sentiments.sentiment_score" }
        }
    },
    { $match: { avg_sentiment: { $gt: 0.7 } } },
    {
        $group: {
            _id: { user_id: "$_id.user_id", list_name: "$_id.list_name" },
            highly_rated_books: {
                $push: { book_id: "$_id.book_id", title: "$_id.book_title", sentiment: "$avg_sentiment" }
            }
        }
    },
    { $sort: { "_id.user_id": 1 } }
]);

// BULK WRITE: Seed multiple activity logs efficiently
db.activity_logs.bulkWrite([
    {
        insertOne: {
            document: {
                user_id: 1, action: "logout", resource_type: "session",
                details: {}, timestamp: new Date()
            }
        }
    },
    {
        insertOne: {
            document: {
                user_id: 2, action: "logout", resource_type: "session",
                details: {}, timestamp: new Date()
            }
        }
    }
]);

// FIND with PROJECTION and LIMIT: Recent activity for a specific user
db.activity_logs.find(
    { user_id: 1 },
    { action: 1, resource_type: 1, timestamp: 1, _id: 0 }
).sort({ timestamp: -1 }).limit(10);
