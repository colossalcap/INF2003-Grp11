# ============================================================
# BookHive — Book Routes (CRUD)
# INF2003 Group 11
# ============================================================

from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models.relational import db, Book, Author, Category, Review
from models.nosql import get_book_metadata, log_activity
from sqlalchemy import or_

books_bp = Blueprint('books', __name__)


@books_bp.route('/')
def list_books():
    """List all books with optional search and category filter."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '', type=int)
    per_page = 12

    query = Book.query

    # Search by title or author
    if search:
        query = query.join(Book.authors).filter(
            or_(
                Book.title.ilike(f'%{search}%'),
                Author.name.ilike(f'%{search}%'),
                Book.isbn.ilike(f'%{search}%')
            )
        ).distinct()

    # Filter by category
    if category_filter:
        query = query.join(Book.categories).filter(Category.category_id == category_filter)

    books = query.order_by(Book.average_rating.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    categories = Category.query.order_by(Category.name).all()

    return render_template('books.html', books=books, categories=categories,
                           search=search, category_filter=category_filter)


@books_bp.route('/<int:book_id>')
def book_detail(book_id):
    """Show details for a single book with reviews."""
    book = Book.query.get_or_404(book_id)

    # Get reviews for this book
    reviews = Review.query.filter_by(book_id=book_id)\
                          .order_by(Review.created_at.desc()).all()

    # Check if current user has already reviewed
    user_review = None
    if 'user_id' in session:
        user_review = Review.query.filter_by(
            book_id=book_id, user_id=session['user_id']
        ).first()

    # Get NoSQL metadata and sentiment stats
    from flask import current_app
    mongo_db = current_app.config.get('_mongo_db')
    metadata = None
    sentiment_stats = None
    if mongo_db:
        metadata = get_book_metadata(mongo_db, book_id)
        from models.nosql import get_book_sentiment_stats
        sentiment_stats = get_book_sentiment_stats(mongo_db, book_id)

        # Log view activity
        if 'user_id' in session:
            log_activity(mongo_db, session['user_id'], 'view_book',
                         resource_type='book', resource_id=book_id,
                         details={'book_title': book.title})

    return render_template('book_detail.html',
                           book=book, reviews=reviews, user_review=user_review,
                           metadata=metadata, sentiment_stats=sentiment_stats)


@books_bp.route('/create', methods=['GET', 'POST'])
def create_book():
    """Create a new book (admin/author only)."""
    if 'user_id' not in session or session.get('role') not in ('admin', 'author'):
        flash('You do not have permission to add books.', 'danger')
        return redirect(url_for('books.list_books'))

    authors = Author.query.order_by(Author.name).all()
    categories = Category.query.order_by(Category.name).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        isbn = request.form.get('isbn', '').strip()
        publisher = request.form.get('publisher', '').strip()
        publication_year = request.form.get('publication_year', type=int)
        page_count = request.form.get('page_count', type=int)
        language = request.form.get('language', 'English')
        description = request.form.get('description', '').strip()
        cover_url = request.form.get('cover_url', '').strip()
        author_ids = request.form.getlist('author_ids')
        category_ids = request.form.getlist('category_ids')

        if not title:
            flash('Book title is required.', 'danger')
            return render_template('create_book.html', authors=authors, categories=categories)

        book = Book(
            title=title, isbn=isbn or None, publisher=publisher,
            publication_year=publication_year, page_count=page_count,
            language=language, description=description, cover_url=cover_url
        )

        # Attach authors (M:M)
        if author_ids:
            book.authors = Author.query.filter(Author.author_id.in_(author_ids)).all()

        # Attach categories (M:M)
        if category_ids:
            book.categories = Category.query.filter(Category.category_id.in_(category_ids)).all()

        db.session.add(book)
        db.session.commit()

        flash(f'"{book.title}" has been added!', 'success')
        return redirect(url_for('books.book_detail', book_id=book.book_id))

    return render_template('create_book.html', authors=authors, categories=categories)
