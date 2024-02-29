from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Book, User, Book_Order
from flask_login import login_required, current_user
from . import db
from sqlalchemy.sql import func

from datetime import timedelta
from .books import update_books_borrowed, get_available_books

book_orders = Blueprint("book_orders", __name__)


# Route for displaying the form to assign a book to a user
@book_orders.route("/assign_book", methods=["GET"])
@login_required
def assign_book_form():
    books = Book.query.all()  
    users = User.query.all()

    book_data = {} 
    for book in books:
        quantity = get_available_books(book.id)
        book_data[book.id] = (quantity)

    return render_template(
        "book_orders/create.html",
        books=books,
        users=users,
        user=current_user,
        book_data=book_data
    )


# Route for processing the form submission to assign a book to a user
@book_orders.route("/assign_book", methods=["POST"])
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

    remaining_books = get_available_books(book_id)

    # Check if the book and user exist, and book is in stock
    if remaining_books <= 2:
        flash("Book is out of stock!", category="error")
        return redirect(url_for("book_orders.assign_book_form"))
    elif check_book_orders(user_id, book_id) == True:
        flash("User has a similar copy of the book!", category="error")
        return redirect(url_for("book_orders.assigned_book_orders"))
    elif book and user:
        # Assign the book to the user
        # ADD BOOK RECORD CUSTOM
        # Create a transaction to update book records on book order success
        if update_books_borrowed(book_id):
            new_book_order = Book_Order(
                issue_date=issue_date,
                fee=book_fee,
                user_id=user_id,
                book_id=book_id,
            )
            db.session.add(new_book_order)
            db.session.commit()
            flash("Book assigned successfully!", category="success")
            return redirect(url_for("book_orders.assigned_book_orders"))
        else:
            flash("Borrowed book update error", category="error")
            return redirect(url_for("book_orders.assign_book_form"))
    else:
        flash("Invalid book or user.", category="error")

    return redirect(url_for("book_orders.assign_book_form"))


# Route for displaying the form to assign a book to a user
@book_orders.route("/assigned_book_orders", methods=["GET"])
@login_required
def assigned_book_orders():
    assigned_books = Book_Order.query.all()
    books = Book.query.all()
    users = User.query.all()

    records_with_details = []

    for record in assigned_books:
        # Calculate fine (30% of charge fee) for days beyond lease time (14 days)
        # days_difference = record.calculate_days_between_dates()
        # if days_difference > record.lease_time:
        #     fine = 0.3 * record.charge_fee * (days_difference - record.lease_time)
        # else:
        #     fine = 0

        # Find the corresponding book and user details
        book = next((b for b in books if b.id == record.book_id), None)
        user = next((u for u in users if u.id == record.user_id), None)

        # Append record details with additional information
        records_with_details.append(
            {
                "id": record.id,
                "issue_date": record.issue_date,
                "return_date": record.return_date,
                "charge_fee": record.book.charge_fee,
                "fine": record.fine,
                "book_id": record.book_id,
                "book_title": book.title if book else None,
                "user_id": record.user_id,
                "user_first_name": user.first_name if user else None,
                "user_last_name": user.last_name if user else None,
            }
        )

    return render_template(
        "book_orders/book_orders.html", records=records_with_details, user=current_user
    )


# check number of times a book has been issued
# def count_book_orders(book_id):
#     with db.session() as session:
#         count = (
#             session.query(func.count(Book_Order.id)).filter_by(book_id=book_id).scalar()
#         )
#         book_quantity = session.query(Book.quantity).filter_by(id=book_id).scalar()
#     return book_quantity, count


# Return book status for each book
# @book_orders.route("/book_count/<int:book_id>", methods=["GET", "POST"])
# def book_stock(book_id):
#     quantity, count = count_book_orders(book_id)
#     return render_template(
#         "book_orders/stock_status.html", quantity=quantity, count=count
#     )


# check if user has borrowed a given book
def check_book_orders(user_id, book_id):
    # Query Book_Order table to check if the user has borrowed the book
    book_order = Book_Order.query.filter_by(user_id=user_id, book_id=book_id).first()

    # Return True if a book record exists, False otherwise
    return book_order is not None


def calculate_days_between_dates(return_date, issue_date):
    days_difference = (return_date - issue_date).days
    return days_difference
