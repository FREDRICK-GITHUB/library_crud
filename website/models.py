from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    phone_no = db.Column(db.String(15), unique=True)  # OK
    is_admin = db.Column(db.Boolean, default=False)  # OK
    password = db.Column(db.String(150))
    book_orders = db.relationship("Book_Order")


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True)
    genre = db.Column(db.String(50))
    authors = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    borrowed = db.Column(db.Integer)
    borrowed_returned = db.Column(db.Integer)
    charge_fee = db.Column(db.Numeric(6, 2))  # OK
    book_orders = db.relationship("Book_Order")


class Book_Order(db.Model):
    __tablename__ = 'book_order'
    id = db.Column(db.Integer, primary_key=True)
    issue_date = db.Column(db.DateTime(timezone=True), default=func.now() )  # make not null
    return_date = db.Column(db.DateTime(timezone=True))  # nullable, updated on book return
    lease_time = db.Column(db.Integer)  # OK
    fee = db.Column(db.Numeric(6, 2))  # OK
    fine = db.Column(db.Numeric(6, 2))  # OK
    payment_status = db.Column(db.Boolean, default=False)  # True if payment paid
    order_status = db.Column(db.Boolean, default=False)  # True if charges paid and book returned
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"))

    book = db.relationship("Book", back_populates="book_orders")
    transaction = db.relationship("Transaction", back_populates="book_order")

    def calculate_days_between_dates(self):
        days_difference = (self.return_date - self.issue_date).days
        return days_difference


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(6, 2))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    order_id = db.Column(db.Integer, db.ForeignKey("book_order.id"))

    book_order = db.relationship("Book_Order", back_populates="transaction", single_parent=True)
