# ============================================================
# BookHive — Application Configuration
# INF2003 Group 11
# ============================================================

import os

class Config:
    """Base configuration."""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Relational Database (SQLite for development, MySQL for production)
    BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASEDIR, "database", "bookhive.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MongoDB
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME', 'bookhive')

    # Session
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

    # Pagination
    BOOKS_PER_PAGE = 12
    REVIEWS_PER_PAGE = 10
