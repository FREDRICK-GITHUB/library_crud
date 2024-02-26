from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.orm import validates

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

    @validates('phone_no')
    def validate_phone_no(self, key, phone_no):
        # Extract last 9 digits from the right and remove any non-digit characters
        normalized_phone_no = ''.join(filter(str.isdigit, phone_no[-9:]))

        # Check if the normalized phone number already exists in the database
        existing_user = User.query.filter_by(phone_no=normalized_phone_no).first()
        if existing_user:
            raise ValueError('Phone number already exists.')

        country_code = '+254'
        final_phone_no = country_code + normalized_phone_no
        return final_phone_no

    
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
    issue_date = db.Column(db.DateTime(timezone=True), default=func.now())
    return_date = db.Column(db.DateTime(timezone=True), default=func.now())
    lease_time = db.Column(db.Integer) #OK
    fee = db.Column(db.Numeric(6,2)) #OK
    fine = db.Column(db.Numeric(6,2)) #OK
    status = db.Column(db.Boolean, default=False) #OK.
    member_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))

    def calculate_days_between_dates(self):
        # Assuming return_date is always greater or equal to issue_date
        days_difference = (self.return_date - self.issue_date).days
        return days_difference
    


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(6,2))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


#//////////------------------------///////////////////////

# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(150), unique=True)
#     first_name = db.Column(db.String(150))
#     last_name = db.Column(db.String(150))
#     password = db.Column(db.String(150))
#     notes = db.relationship('Note')

# class Note(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     data  = db.Column(db.String(10000))
#     date = db.Column(db.DateTime(timezone=True), default=func.now())
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))