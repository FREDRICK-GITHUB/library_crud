from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Book
from flask_login import login_required, current_user
from . import db



books = Blueprint("books", __name__)


@books.route("/view_books", methods=["GET", "POST"])
@login_required
def home():
    books = Book.query.all()

    return render_template(
        "books/books.html", books=books, user=current_user
    )


@books.route("/create_new_book", methods=["GET", "POST"])
@login_required
def createNewBook():
    if request.method == "POST":
        title = request.form.get("title")
        genre = request.form.get("genre")
        authors = request.form.get("authors")
        charge_fee = request.form.get("charge_fee")
        quantity = request.form.get("quantity")

        book = Book.query.filter_by(title=title).first()
        if book:
            flash("Book with that title exists!", category="error")
        elif len(title) < 3:
            flash("Title must have at least 4 characters.", category="error")
        elif len(genre) < 3:
            flash("Genre must have at least 4 characters.", category="error")
        elif len(authors) < 4:
            flash("Author name must be more than 4 characters.", category="error")
        elif int(charge_fee) < 1:
            flash("Charge fee should be a positive integer.", category="error")
        elif int(quantity) < 1:
            flash("Quantity cannot be zero for exisiting books!", category="error")
        else:
            new_book = Book(
                title=title,
                genre=genre,
                authors=authors,
                quantity=quantity,
                borrowed=0,
                borrowed_returned=0,
                charge_fee=charge_fee,
            )
            db.session.add(new_book)
            db.session.commit()
            flash("New book added!", category="success")
            return redirect(url_for("books.home"))

    return render_template("books/create.html", user=current_user)


@books.route("/update_books_borrowed", methods=["POST"])
@login_required
def update_books_borrowed(book_id):
    # Retrieve the book object by its ID
    book = Book.query.get(book_id)
    
    if book:
        # Increment the borrowed field
        book.borrowed += 1
        
        # Commit the changes to the database
        try:
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False
    else:
        return False
    
    
def get_available_books(book_id):
    # Retrieve the book object by its ID
    book = Book.query.get(book_id)
    
    if book:
        # Calculate the number of available books
        available_books = book.quantity - (book.borrowed - book.borrowed_returned)
        return available_books
    else:
        return None