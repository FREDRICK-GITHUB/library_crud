from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Book, User, Book_Record 
from flask_login import login_required, current_user
from . import db
import json

book_records = Blueprint("book_records", __name__)

# Route for displaying the form to assign a book to a user
@book_records.route('/assign_book', methods=['GET'])
@login_required
def assign_book_form():
    books = Book.query.all()  # Fetch all books from the database
    users = User.query.all()  # Fetch all users from the database
    return render_template('book_records/create.html', books=books, users=users, user=current_user)

# Route for processing the form submission to assign a book to a user
@book_records.route('/assign_book', methods=['POST'])
@login_required
def assign_book():
    book_id = request.form.get('book_id')
    user_id = request.form.get('user_id')
    
    # Fetch the book and user objects from the database
    book = Book.query.get(book_id)
    user = User.query.get(user_id)
    
    # Check if the book and user exist
    if book and user:
        # Assign the book to the user
        # ADD BOOK RECORD CUSTOM CODE
        user.books.append(book)
        db.session.commit()
        flash('Book assigned successfully!', category='success')
    else:
        flash('Invalid book or user.', category='error')
    
    return redirect(url_for('assign_book_form'))

