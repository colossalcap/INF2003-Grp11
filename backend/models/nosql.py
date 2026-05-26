# ============================================================
# BookHive — MongoDB (NoSQL) Helper Functions
# INF2003 Group 11
# ============================================================

from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId


def get_mongo_client(uri='mongodb://localhost:27017/'):
    """Create and return a MongoDB client connection."""
    return MongoClient(uri)


def init_mongo_indexes(db):
    """Create indexes on MongoDB collections for performance."""
    # reading_lists indexes
    db.reading_lists.create_index([('user_id', 1), ('list_name', 1)], unique=True)
    db.reading_lists.create_index([('books.book_id', 1)])
    db.reading_lists.create_index([('is_public', 1)])

    # review_sentiments indexes
    db.review_sentiments.create_index([('review_id', 1)], unique=True)
    db.review_sentiments.create_index([('book_id', 1), ('sentiment_label', 1)])
    db.review_sentiments.create_index([('analyzed_at', -1)])

    # book_metadata indexes
    db.book_metadata.create_index([('book_id', 1)], unique=True)
    db.book_metadata.create_index([('tags', 1)])
    db.book_metadata.create_index([('awards.name', 1)])

    # activity_logs indexes
    db.activity_logs.create_index([('user_id', 1), ('timestamp', -1)])
    db.activity_logs.create_index([('timestamp', -1)])
    db.activity_logs.create_index([('action', 1), ('timestamp', -1)])

    print("✅ MongoDB indexes initialized.")


# ------------------------------------------------------------
# Reading Lists CRUD
# ------------------------------------------------------------
def create_reading_list(mongo_db, user_id, list_name, description='', is_public=True):
    """Create a new reading list for a user."""
    doc = {
        'user_id': user_id,
        'list_name': list_name,
        'description': description,
        'is_public': is_public,
        'books': [],
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    return mongo_db.reading_lists.insert_one(doc)


def get_user_reading_lists(mongo_db, user_id, include_private=True):
    """Get all reading lists for a user."""
    query = {'user_id': user_id}
    if not include_private:
        query['is_public'] = True
    return list(mongo_db.reading_lists.find(query).sort('updated_at', -1))


def get_reading_list(mongo_db, user_id, list_name):
    """Get a specific reading list."""
    return mongo_db.reading_lists.find_one({'user_id': user_id, 'list_name': list_name})


def add_book_to_list(mongo_db, user_id, list_name, book_id, title, isbn, notes=''):
    """Add a book to an existing reading list."""
    return mongo_db.reading_lists.update_one(
        {'user_id': user_id, 'list_name': list_name},
        {
            '$push': {
                'books': {
                    'book_id': book_id,
                    'title': title,
                    'isbn': isbn,
                    'added_at': datetime.utcnow(),
                    'notes': notes
                }
            },
            '$set': {'updated_at': datetime.utcnow()}
        }
    )


def remove_book_from_list(mongo_db, user_id, list_name, book_id):
    """Remove a book from a reading list."""
    return mongo_db.reading_lists.update_one(
        {'user_id': user_id, 'list_name': list_name},
        {'$pull': {'books': {'book_id': book_id}}}
    )


def delete_reading_list(mongo_db, user_id, list_name):
    """Delete an entire reading list."""
    return mongo_db.reading_lists.delete_one({'user_id': user_id, 'list_name': list_name})


# ------------------------------------------------------------
# Book Metadata CRUD
# ------------------------------------------------------------
def get_book_metadata(mongo_db, book_id):
    """Get flexible metadata for a book."""
    return mongo_db.book_metadata.find_one({'book_id': book_id})


def search_books_by_tag(mongo_db, tag):
    """Find books matching a specific tag."""
    return list(mongo_db.book_metadata.find({'tags': tag}, {'book_id': 1, 'tags': 1}))


# ------------------------------------------------------------
# Activity Logging
# ------------------------------------------------------------
def log_activity(mongo_db, user_id, action, resource_type=None, resource_id=None, details=None, ip_address=None):
    """Record a user activity event."""
    doc = {
        'user_id': user_id,
        'action': action,
        'resource_type': resource_type,
        'resource_id': resource_id,
        'details': details or {},
        'ip_address': ip_address,
        'timestamp': datetime.utcnow()
    }
    return mongo_db.activity_logs.insert_one(doc)


def get_user_activity(mongo_db, user_id, limit=20):
    """Get recent activity for a user."""
    return list(
        mongo_db.activity_logs.find({'user_id': user_id})
        .sort('timestamp', -1)
        .limit(limit)
    )


# ------------------------------------------------------------
# Review Sentiments
# ------------------------------------------------------------
def get_book_sentiment_stats(mongo_db, book_id):
    """Get aggregated sentiment statistics for a book."""
    pipeline = [
        {'$match': {'book_id': book_id}},
        {
            '$group': {
                '_id': '$sentiment_label',
                'count': {'$sum': 1},
                'avg_score': {'$avg': '$sentiment_score'}
            }
        }
    ]
    return list(mongo_db.review_sentiments.aggregate(pipeline))


# ------------------------------------------------------------
# Analytics / Aggregation Helpers
# ------------------------------------------------------------
def get_popular_keywords(mongo_db, limit=10):
    """Get the most frequently mentioned positive keywords across reviews."""
    pipeline = [
        {'$match': {'sentiment_label': 'positive'}},
        {'$unwind': '$keywords'},
        {'$group': {'_id': '$keywords', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': limit}
    ]
    return list(mongo_db.review_sentiments.aggregate(pipeline))


def get_user_reading_stats(mongo_db, user_id):
    """Get aggregate reading statistics for a user."""
    pipeline = [
        {'$match': {'user_id': user_id}},
        {'$unwind': '$books'},
        {
            '$group': {
                '_id': '$user_id',
                'total_books': {'$sum': 1},
                'unique_books': {'$addToSet': '$books.book_id'},
                'lists_used': {'$addToSet': '$list_name'}
            }
        },
        {
            '$project': {
                '_id': 0,
                'total_books': 1,
                'unique_count': {'$size': '$unique_books'},
                'list_count': {'$size': '$lists_used'}
            }
        }
    ]
    result = list(mongo_db.reading_lists.aggregate(pipeline))
    return result[0] if result else None
