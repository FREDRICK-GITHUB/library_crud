from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .models import Book, User, Book_Order, Transaction
from flask_login import login_required, current_user
from . import db
from sqlalchemy.sql import func

from datetime import datetime
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
    issue_date = func.now().strftime('%Y-%m-%d %H:%M:%S')

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


# check if user has borrowed a given book
def check_book_orders(user_id, book_id):
    # Query Book_Order table to check if the user has borrowed the book
    book_order = Book_Order.query.filter_by(user_id=user_id, book_id=book_id).first()

    # Return True if a book record exists, False otherwise
    return book_order is not None


def calculate_days_between_dates(return_date, issue_date):
    days_difference = (return_date - issue_date).days
    return days_difference


@book_orders.route("/get_order_details/<int:book_id>/<int:user_id>/", methods=["GET","POST"])
@login_required
def get_user_details(book_id, user_id):
    # Query the Book_Order, Book, and User tables to get the required information
    book_order = Book_Order.query.filter_by(book_id=book_id, user_id=user_id).first()

    if book_order:
        # Retrieve book and user details
        book = Book.query.get(book_id)
        user = User.query.get(user_id)

        lease_time = (datetime.now() - book_order.issue_date).days
        return_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if lease_time <= 14:
            fine = 0
        else:
            fine = 0.3 * book_order.fee * (lease_time - 14)

        total_transaction_amount = book_order.fee + fine

        # Construct response data
        response_data = {
            'order_id': book_order.id,
            'book_id': book.id,
            'book_title': book.title,
            'issue_date': book_order.issue_date,
            'user_id': user.id,
            'user_email': user.email,
            'user_first_name': user.first_name,
            'user_last_name': user.last_name,
            'return_date': return_date,
            'lease_time': lease_time,
            'total_fine': fine,
            'total_amount': total_transaction_amount
        }

        # data =  jsonify(response_data)
        return render_template("book_orders/book_order_details.html", data=response_data ,user=current_user)
    else:
        flash('Book order not found for the given book and user.', category="error")
        return redirect(url_for('users.home'))
    

@book_orders.route("/complete_return/", methods=["GET","POST"])
@login_required
def complete_return():
    book_id = request.form.get('book_id')
    user_id = request.form.get('user_id')

    # returned = request.form.get('return_date')
    returned_str = request.form.get('return_date')
    returned = datetime.strptime(returned_str, '%Y-%m-%d %H:%M:%S')
    return_date = returned.date()

    lease = request.form.get('lease_time')
    amount = request.form.get('total_amount')
    fine = request.files.get('total_fine')

    # Query the Book_Order, Book, and User tables to get the required information
    book_order = Book_Order.query.filter_by(book_id=book_id, user_id=user_id).first()

    if book_order:
        try:
            # Update the borrowed_returned field of the Book
            book = Book.query.get(book_id)
            if book:
                book.borrowed_returned += 1

            # Create a new Transaction
            new_transaction = Transaction(amount=amount, date=return_date, order_id=book_order.id)

            # Update the Book_Order record
            book_order.return_date = returned
            book_order.lease_time = lease
            book_order.fine = fine
            book_order.payment_status = True
            book_order.order_status = True

            # Add all changes to the session
            db.session.add(new_transaction)
            db.session.commit()

            flash("Book Return completed!", category="success")
            return redirect(url_for("book_orders.completed_returns"))
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    else:
        flash("Book order not found.", category="error")
        return redirect(url_for('book_orders.assigned_book_orders'))
    

@book_orders.route("/view_return_records", methods=["GET"])
@login_required
def completed_returns():
    complete_orders = Book_Order.query.filter_by(order_status=True).all()
    books = Book.query.all()
    users = User.query.all()

    records_with_details = []

    for record in complete_orders:
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
    return render_template("book_orders/complete_orders.html", complete_orders=records_with_details, user=current_user)