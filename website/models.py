from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.orm import validates
from flask import flash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    phone_no = db.Column(db.String(15), unique=True) #OK
    is_admin = db.Column(db.Boolean, default=False) # OK
    password = db.Column(db.String(150))
    book_records = db.relationship('Book_Record')
    transactions = db.relationship('Transaction')

    
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True)
    genre = db.Column(db.String(50))
    authors = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    charge_fee = db.Column(db.Numeric(6,2)) #OK
    book_records = db.relationship('Book_Record')
    

class Book_Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    issue_date = db.Column(db.DateTime(timezone=True), default=func.now(), ) #make not null
    return_date = db.Column(db.DateTime(timezone=True), default=func.now())
    lease_time = db.Column(db.Integer) #OK
    fee = db.Column(db.Numeric(6,2)) #OK
    fine = db.Column(db.Numeric(6,2)) #OK
    status = db.Column(db.Boolean, default=False) #OK.
    member_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    book = db.relationship("Book", back_populates="book_records")

    def calculate_days_between_dates(self):
        days_difference = (self.return_date - self.issue_date).days
        return days_difference
    


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(6,2))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
