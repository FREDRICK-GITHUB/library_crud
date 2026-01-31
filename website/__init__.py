from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash

load_dotenv()
db = SQLAlchemy()
DB_NAME = os.getenv("DB_NAME", "library_solution.db")


def create_app():
    app = Flask(__name__)

    # Configuration
    secret = os.getenv("SECRET_KEY")
    if not secret:
        raise ValueError("SECRET_KEY environment variable is not set")

    app.config["SECRET_KEY"] = secret

    # Database configuration - use absolute path for production
    db_path = os.getenv("DATABASE_PATH", os.path.join(os.getcwd(), "instance", DB_NAME))
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Production settings
    app.config["SESSION_COOKIE_SECURE"] = (
        os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    )
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    db.init_app(app)

    from .views import views
    from .auth import auth
    from .users import users
    from .books import books
    from .book_orders import book_orders
    from .transactions import transactions

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(users, url_prefix="/")
    app.register_blueprint(books, url_prefix="/")
    app.register_blueprint(book_orders, url_prefix="/")
    app.register_blueprint(transactions, url_prefix="/")

    from .models import User

    with app.app_context():
        db.create_all()
        create_default_admin()
        create_sample_books()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists("website/" + DB_NAME):
        db.create_all(app=app)
        print("Created Database!")


def create_default_admin():
    """
    Create default admin user with proper race condition handling.
    Safe for multiple workers in Kubernetes/production environments.
    """
    from .models import User
    from sqlalchemy.exc import IntegrityError

    admin_email = "admin@quickmail.com"
    admin_phone = "+254711223344"

    try:
        # Use with_for_update() to acquire row-level lock during check
        # This prevents race conditions between multiple workers
        existing = (
            User.query.filter(
                (User.email == admin_email) | (User.phone_no == admin_phone)
            )
            .with_for_update()
            .first()
        )

        if existing:
            # Admin already exists, safe to return
            db.session.rollback()
            return

        # Create admin user
        default_password = "1234567"
        hashed_password = generate_password_hash(
            default_password, method="pbkdf2:sha256"
        )
        admin = User(
            email=admin_email,
            first_name="Admin",
            last_name="User",
            phone_no=admin_phone,
            is_admin=True,
            password=hashed_password,
        )
        db.session.add(admin)
        db.session.commit()

    except IntegrityError:
        # Another worker created the admin between our check and insert
        # This is expected in multi-worker environments - safe to ignore
        db.session.rollback()
    except Exception as e:
        # Log unexpected errors but don't crash the application
        db.session.rollback()
        print(f"Warning: Could not create default admin: {e}")
        # Application continues - admin might already exist or will be created manually


def create_sample_books():
    """
    Create sample books with proper race condition handling.
    Safe for multiple workers in Kubernetes/production environments.
    """
    from .models import Book
    from sqlalchemy.exc import IntegrityError

    books_data = [
        {
            "title": "48 Laws of Power",
            "genre": "Motivation",
            "authors": "Robert Greene",
            "quantity": 25,
            "borrowed": 0,
            "borrowed_returned": 0,
            "charge_fee": 200.00,
        },
        {
            "title": "Atomic Habits",
            "genre": "Self Help",
            "authors": "James Clear",
            "quantity": 35,
            "borrowed": 0,
            "borrowed_returned": 0,
            "charge_fee": 250.00,
        },
        {
            "title": "Mastery",
            "genre": "Motivation",
            "authors": "Robert Greene",
            "quantity": 15,
            "borrowed": 0,
            "borrowed_returned": 0,
            "charge_fee": 300.00,
        },
    ]

    try:
        # Check if any books exist with row-level lock
        existing_count = Book.query.with_for_update().count()

        if existing_count > 0:
            # Books already exist, safe to return
            db.session.rollback()
            return

        # Create sample books
        for book_data in books_data:
            book = Book(**book_data)
            db.session.add(book)

        db.session.commit()

    except IntegrityError:
        # Another worker created books between our check and insert
        # This is expected in multi-worker environments - safe to ignore
        db.session.rollback()
    except Exception as e:
        # Log unexpected errors but don't crash the application
        db.session.rollback()
        print(f"Warning: Could not create sample books: {e}")
        # Application continues - books might already exist or will be created manually
