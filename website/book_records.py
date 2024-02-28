from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Book, User, Book_Record
from flask_login import login_required, current_user
from . import db
from sqlalchemy.sql import func

book_records = Blueprint("book_records", __name__)


# Route for displaying the form to assign a book to a user
@book_records.route("/assign_book", methods=["GET"])
@login_required
def assign_book_form():
    books = Book.query.all()  # Fetch all books from the database
    users = User.query.all()  # Fetch all users from the database
    book_data = {}  

    for book in books:
        quantity, count = count_book_records(book.id)
        in_stock = quantity - count
        book_data[book.id] = (quantity, count, in_stock)

    return render_template(
        "book_records/create.html", 
        books=books, 
        users=users, 
        user=current_user,
        book_data=book_data
    )


# Route for processing the form submission to assign a book to a user
@book_records.route("/assign_book", methods=["POST"])
@login_required
def assign_book():
    book_id = request.form.get("book_id")
    user_id = request.form.get("user_id")

    # Fetch the book and user objects from the database
    book = Book.query.get(book_id)
    user = User.query.get(user_id)

    user_id = user.id
    book_fee = book.charge_fee
    book_id = book.id
    default_lease_time = (
        14  # days from issue date, fine is 30% of charge fee every extra day
    )
    issue_date = func.now()

    book_quantity, count = count_book_records(book_id)
    remaining_books = book_quantity - count

    # Check if the book and user exist, and book is in stock
    if remaining_books <= 2:
        flash("Book is out of stock!", category="error")
        return redirect(url_for("book_records.assign_book_form"))
    elif check_book_record(user_id, book_id) == True:
        flash("User has a similar copy of the book!", category="error")
        return redirect(url_for("book_records.assigned_book_records"))
    elif book and user:
        # Assign the book to the user
        # ADD BOOK RECORD CUSTOM
        new_book_record = Book_Record(
            issue_date=issue_date,
            lease_time=default_lease_time,
            fee=book_fee,
            status=False,
            member_id=user_id,
            book_id=book_id,
        )
        db.session.add(new_book_record)
        db.session.commit()
        flash("Book assigned successfully!", category="success")
        return redirect(url_for("book_records.assigned_book_records"))
    else:
        flash("Invalid book or user.", category="error")

    return redirect(url_for("book_records.assign_book_form"))


# Route for displaying the form to assign a book to a user
@book_records.route("/assigned_book_records", methods=["GET"])
@login_required
def assigned_book_records():
    assigned_books = Book_Record.query.all() 
    books = Book.query.all()
    users = User.query.all() 

    records_with_details = []

    for record in assigned_books:
        # Calculate fine (30% of charge fee) for days beyond lease time (14 days)
        days_difference = record.calculate_days_between_dates()
        if days_difference > record.lease_time:
            fine = 0.3 * record.charge_fee * (days_difference - record.lease_time)
        else:
            fine = 0
        
        # Find the corresponding book and user details
        book = next((b for b in books if b.id == record.book_id), None)
        user = next((u for u in users if u.id == record.member_id), None)
        
        # Append record details with additional information
        records_with_details.append({
            'id': record.id,
            'issue_date': record.issue_date,
            'return_date': record.return_date,
            'charge_fee': record.book.charge_fee,
            'fine': fine,
            'book_id': record.book_id,
            'book_title': book.title if book else None,
            'user_id': record.member_id,
            'user_first_name': user.first_name if user else None,
            'user_last_name': user.last_name if user else None
        })


    
    return render_template(
        "book_records/book_records.html", 
        records=records_with_details, 
        user=current_user
    )


#check number of times a book has been issued
def count_book_records(book_id):
    with db.session() as session:
        count = session.query(func.count(Book_Record.id)).filter_by(book_id=book_id).scalar()
        book_quantity = session.query(Book.quantity).filter_by(id=book_id).scalar()
    return book_quantity, count

#Return book status for each book
@book_records.route('/book_count/<int:book_id>', methods=["GET","POST"])
def book_stock(book_id):
    quantity, count = count_book_records(book_id)
    return render_template('book_records/stock_status.html', quantity=quantity, count=count)

#check if user has borrowed a given book
def check_book_record(user_id, book_id):
    # Query Book_Record table to check if the user has borrowed the book
    book_record = Book_Record.query.filter_by(member_id=user_id, book_id=book_id).first()

    # Return True if a book record exists, False otherwise
    return book_record is not None