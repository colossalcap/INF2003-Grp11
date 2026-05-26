# ============================================================
# BookHive — Flask Application Entry Point
# INF2003 Group 11
# ============================================================

from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from config import Config
from models.relational import db, User, Book, Author, Category, Review
from models.nosql import get_mongo_client, init_mongo_indexes

# Import route blueprints
from routes.auth import auth_bp
from routes.books import books_bp
from routes.reviews import reviews_bp
from routes.reading_lists import reading_lists_bp

# --- App Initialization ---
app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.config.from_object(Config)

# --- Extensions ---
db.init_app(app)
bcrypt = Bcrypt(app)

# --- Register Blueprints ---
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(books_bp, url_prefix='/books')
app.register_blueprint(reviews_bp, url_prefix='/reviews')
app.register_blueprint(reading_lists_bp, url_prefix='/lists')

# --- MongoDB Initialization ---
mongo_client = None
mongo_db = None

def get_mongo_db():
    """Lazy-load MongoDB connection."""
    global mongo_client, mongo_db
    if mongo_client is None:
        mongo_client = get_mongo_client(app.config['MONGO_URI'])
        mongo_db = mongo_client[app.config['MONGO_DB_NAME']]
        init_mongo_indexes(mongo_db)
    return mongo_db

# Make MongoDB available to blueprints
@app.context_processor
def inject_mongo():
    return {'mongo_db': get_mongo_db()}

# --- Routes ---

@app.route('/')
def index():
    """Homepage — displays featured books."""
    featured_books = Book.query.order_by(Book.average_rating.desc()).limit(6).all()
    return render_template('index.html', books=featured_books)

@app.route('/about')
def about():
    return render_template('about.html')

# --- Context Processor ---
@app.context_processor
def inject_user():
    """Make current user available to all templates."""
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return {'current_user': user}

# --- Error Handlers ---
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# --- Run ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Relational database tables created.")
    app.run(debug=True, host='0.0.0.0', port=5000)
