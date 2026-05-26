# ============================================================
# BookHive — SQLAlchemy Relational Models
# INF2003 Group 11
# ============================================================

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ------------------------------------------------------------
# Junction Tables (M:M relationships)
# ------------------------------------------------------------
book_authors = db.Table(
    'book_authors',
    db.Column('book_id', db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), primary_key=True),
    db.Column('author_id', db.Integer, db.ForeignKey('authors.author_id', ondelete='CASCADE'), primary_key=True)
)

book_categories = db.Table(
    'book_categories',
    db.Column('book_id', db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.category_id', ondelete='CASCADE'), primary_key=True)
)

# ------------------------------------------------------------
# User Model
# ------------------------------------------------------------
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))
    role = db.Column(db.String(20), default='reader')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationships
    reviews = db.relationship('Review', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

# ------------------------------------------------------------
# Author Model
# ------------------------------------------------------------
class Author(db.Model):
    __tablename__ = 'authors'

    author_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    biography = db.Column(db.Text)
    birth_date = db.Column(db.Date)
    nationality = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    books = db.relationship('Book', secondary=book_authors, backref=db.backref('authors', lazy='dynamic'))

    def __repr__(self):
        return f'<Author {self.name}>'

# ------------------------------------------------------------
# Category Model
# ------------------------------------------------------------
class Category(db.Model):
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    parent_category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='SET NULL'))

    # Self-referencing relationship (hierarchical categories)
    parent = db.relationship('Category', remote_side=[category_id], backref='subcategories')

    # Relationships
    books = db.relationship('Book', secondary=book_categories, backref=db.backref('categories', lazy='dynamic'))

    def __repr__(self):
        return f'<Category {self.name}>'

# ------------------------------------------------------------
# Book Model
# ------------------------------------------------------------
class Book(db.Model):
    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), unique=True)
    title = db.Column(db.String(255), nullable=False)
    publisher = db.Column(db.String(100))
    publication_year = db.Column(db.Integer)
    page_count = db.Column(db.Integer)
    language = db.Column(db.String(30), default='English')
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(255))
    average_rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    reviews = db.relationship('Review', backref='book', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Book {self.title}>'

# ------------------------------------------------------------
# Review Model
# ------------------------------------------------------------
class Review(db.Model):
    __tablename__ = 'reviews'

    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200))
    body = db.Column(db.Text)
    spoiler_alert = db.Column(db.Boolean, default=False)
    helpful_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Ensure one review per user per book
    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id', name='uq_user_book_review'),
    )

    def __repr__(self):
        return f'<Review {self.review_id} by User {self.user_id}>'
