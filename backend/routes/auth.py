# ============================================================
# BookHive — Authentication Routes
# INF2003 Group 11
# ============================================================

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from models.relational import db, User
from models.nosql import log_activity
from datetime import datetime

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['role'] = user.role

            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()

            # Log activity to MongoDB
            from flask import current_app
            mongo_db = current_app.config.get('_mongo_db')
            if mongo_db:
                log_activity(mongo_db, user.user_id, 'login',
                             resource_type='session',
                             ip_address=request.remote_addr)

            flash(f'Welcome back, {user.display_name or user.username}!', 'success')
            return redirect(url_for('index'))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        display_name = request.form.get('display_name', '').strip()

        # Validation
        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm_password:
            errors.append('Passwords do not match.')

        # Check uniqueness
        if User.query.filter_by(username=username).first():
            errors.append('Username already taken.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html')

        # Create user
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_pw,
            display_name=display_name or username,
            role='reader'
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    """Log out current user."""
    user_id = session.get('user_id')

    if user_id:
        from flask import current_app
        mongo_db = current_app.config.get('_mongo_db')
        if mongo_db:
            log_activity(mongo_db, user_id, 'logout', resource_type='session')

    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
