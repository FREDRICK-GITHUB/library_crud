from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash

load_dotenv()
db = SQLAlchemy()
DB_NAME = os.getenv("DB_NAME")


def create_app():
    app = Flask(__name__)
    secret = os.getenv("SECRET_KEY")
    app.config["SECRET_KEY"] = secret
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
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
    from .models import User

    # Check if an admin user already exists
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        return

    default_password = "1234567"
    hashed_password = generate_password_hash(default_password, method="pbkdf2:sha256")

    admin = User(
        email="admin@quickmail.com",
        first_name="Admin",
        last_name="User",
        phone_no="+254711223344",
        is_admin=True,
        password=hashed_password,
    )
    db.session.add(admin)
    db.session.commit()
