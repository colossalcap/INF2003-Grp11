# ============================================================
# BookHive — Reading List Routes (NoSQL CRUD)
# INF2003 Group 11
# ============================================================

from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models.nosql import (
    create_reading_list, get_user_reading_lists, get_reading_list,
    add_book_to_list, remove_book_from_list, delete_reading_list,
    log_activity, get_user_reading_stats
)
from models.relational import Book

reading_lists_bp = Blueprint('reading_lists', __name__)


def _get_mongo():
    """Helper to get MongoDB database from app context."""
    from flask import current_app
    return current_app.config.get('_mongo_db')


@reading_lists_bp.route('/')
def my_lists():
    """Show all reading lists for the current user."""
    if 'user_id' not in session:
        flash('Please log in to view your reading lists.', 'warning')
        return redirect(url_for('auth.login'))

    mongo_db = _get_mongo()
    if not mongo_db:
        flash('Reading lists are temporarily unavailable.', 'danger')
        return redirect(url_for('index'))

    user_id = session['user_id']
    lists = get_user_reading_lists(mongo_db, user_id)
    stats = get_user_reading_stats(mongo_db, user_id)

    return render_template('reading_lists.html', lists=lists, stats=stats)


@reading_lists_bp.route('/create', methods=['GET', 'POST'])
def create_list():
    """Create a new reading list."""
    if 'user_id' not in session:
        flash('Please log in.', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        mongo_db = _get_mongo()
        list_name = request.form.get('list_name', '').strip()
        description = request.form.get('description', '').strip()
        is_public = request.form.get('is_public') == 'on'

        if not list_name:
            flash('List name is required.', 'danger')
            return render_template('create_list.html')

        # Check for duplicate
        existing = get_reading_list(mongo_db, session['user_id'], list_name)
        if existing:
            flash(f'You already have a list named "{list_name}".', 'danger')
            return render_template('create_list.html')

        create_reading_list(mongo_db, session['user_id'], list_name, description, is_public)

        log_activity(mongo_db, session['user_id'], 'create_list',
                     resource_type='reading_list',
                     details={'list_name': list_name})

        flash(f'Reading list "{list_name}" created!', 'success')
        return redirect(url_for('reading_lists.my_lists'))

    return render_template('create_list.html')


@reading_lists_bp.route('/<list_name>')
def view_list(list_name):
    """View a specific reading list."""
    if 'user_id' not in session:
        flash('Please log in.', 'warning')
        return redirect(url_for('auth.login'))

    mongo_db = _get_mongo()
    reading_list = get_reading_list(mongo_db, session['user_id'], list_name)
    if not reading_list:
        flash('Reading list not found.', 'danger')
        return redirect(url_for('reading_lists.my_lists'))

    return render_template('view_list.html', reading_list=reading_list)


@reading_lists_bp.route('/<list_name>/add/<int:book_id>', methods=['POST'])
def add_book(list_name, book_id):
    """Add a book to a reading list."""
    if 'user_id' not in session:
        flash('Please log in.', 'warning')
        return redirect(url_for('auth.login'))

    mongo_db = _get_mongo()
    book = Book.query.get_or_404(book_id)
    notes = request.form.get('notes', '').strip()

    add_book_to_list(mongo_db, session['user_id'], list_name,
                     book.book_id, book.title, book.isbn, notes)

    log_activity(mongo_db, session['user_id'], 'add_to_list',
                 resource_type='reading_list',
                 details={'list_name': list_name, 'book_id': book_id, 'book_title': book.title})

    flash(f'"{book.title}" added to {list_name}!', 'success')
    return redirect(request.referrer or url_for('reading_lists.my_lists'))


@reading_lists_bp.route('/<list_name>/remove/<int:book_id>', methods=['POST'])
def remove_book(list_name, book_id):
    """Remove a book from a reading list."""
    if 'user_id' not in session:
        flash('Please log in.', 'warning')
        return redirect(url_for('auth.login'))

    mongo_db = _get_mongo()
    remove_book_from_list(mongo_db, session['user_id'], list_name, book_id)

    flash('Book removed from list.', 'info')
    return redirect(url_for('reading_lists.view_list', list_name=list_name))


@reading_lists_bp.route('/<list_name>/delete', methods=['POST'])
def delete_list(list_name):
    """Delete an entire reading list."""
    if 'user_id' not in session:
        flash('Please log in.', 'warning')
        return redirect(url_for('auth.login'))

    mongo_db = _get_mongo()
    delete_reading_list(mongo_db, session['user_id'], list_name)

    flash(f'Reading list "{list_name}" deleted.', 'info')
    return redirect(url_for('reading_lists.my_lists'))
