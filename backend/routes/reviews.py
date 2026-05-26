# ============================================================
# BookHive — Review Routes (CRUD)
# INF2003 Group 11
# ============================================================

from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models.relational import db, Review, Book, User
from models.nosql import log_activity
from datetime import datetime

reviews_bp = Blueprint('reviews', __name__)


@reviews_bp.route('/create/<int:book_id>', methods=['GET', 'POST'])
def create_review(book_id):
    """Create a new review for a book."""
    if 'user_id' not in session:
        flash('Please log in to write a review.', 'warning')
        return redirect(url_for('auth.login'))

    book = Book.query.get_or_404(book_id)
    user_id = session['user_id']

    # Check if user already reviewed this book
    existing = Review.query.filter_by(user_id=user_id, book_id=book_id).first()
    if existing:
        flash('You have already reviewed this book. You can edit your review instead.', 'info')
        return redirect(url_for('reviews.edit_review', review_id=existing.review_id))

    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        title = request.form.get('title', '').strip()
        body = request.form.get('body', '').strip()
        spoiler_alert = request.form.get('spoiler_alert') == 'on'

        if not rating or rating < 1 or rating > 5:
            flash('Please provide a rating between 1 and 5.', 'danger')
            return render_template('create_review.html', book=book)

        review = Review(
            user_id=user_id,
            book_id=book_id,
            rating=rating,
            title=title,
            body=body,
            spoiler_alert=spoiler_alert
        )
        db.session.add(review)

        # The trigger will auto-update book.average_rating
        db.session.commit()

        # Log to MongoDB
        from flask import current_app
        mongo_db = current_app.config.get('_mongo_db')
        if mongo_db:
            log_activity(mongo_db, user_id, 'write_review',
                         resource_type='review',
                         resource_id=review.review_id,
                         details={'book_id': book_id, 'rating': rating})

        flash('Your review has been posted!', 'success')
        return redirect(url_for('books.book_detail', book_id=book_id))

    return render_template('create_review.html', book=book)


@reviews_bp.route('/edit/<int:review_id>', methods=['GET', 'POST'])
def edit_review(review_id):
    """Edit an existing review."""
    if 'user_id' not in session:
        flash('Please log in.', 'warning')
        return redirect(url_for('auth.login'))

    review = Review.query.get_or_404(review_id)

    # Only the review author or admin can edit
    if review.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('You can only edit your own reviews.', 'danger')
        return redirect(url_for('books.book_detail', book_id=review.book_id))

    if request.method == 'POST':
        review.rating = request.form.get('rating', type=int, default=review.rating)
        review.title = request.form.get('title', '').strip()
        review.body = request.form.get('body', '').strip()
        review.spoiler_alert = request.form.get('spoiler_alert') == 'on'

        db.session.commit()
        flash('Review updated!', 'success')
        return redirect(url_for('books.book_detail', book_id=review.book_id))

    return render_template('edit_review.html', review=review)


@reviews_bp.route('/delete/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    """Delete a review."""
    if 'user_id' not in session:
        flash('Please log in.', 'warning')
        return redirect(url_for('auth.login'))

    review = Review.query.get_or_404(review_id)

    if review.user_id != session['user_id'] and session.get('role') != 'admin':
        flash('You can only delete your own reviews.', 'danger')
        return redirect(url_for('books.book_detail', book_id=review.book_id))

    book_id = review.book_id
    db.session.delete(review)
    db.session.commit()

    flash('Review deleted.', 'info')
    return redirect(url_for('books.book_detail', book_id=book_id))


@reviews_bp.route('/helpful/<int:review_id>', methods=['POST'])
def mark_helpful(review_id):
    """Increment the helpful count on a review."""
    review = Review.query.get_or_404(review_id)
    review.helpful_count = (review.helpful_count or 0) + 1
    db.session.commit()
    flash('Marked as helpful!', 'success')
    return redirect(url_for('books.book_detail', book_id=review.book_id))
