from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User, Book_Order, Transaction
from flask_login import login_required, current_user
from . import db
from datetime import datetime

users = Blueprint("users", __name__)

@users.route("/view_users", methods=["GET", "POST"])
@login_required
def home():
    members = User.query.all()
    return render_template("users/read.html", members=members, user=current_user)


@users.route("/create_new_user", methods=["GET", "POST"])
@login_required
def createNewUser():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        last_name = request.form.get("lastName")
        phone_no = request.form.get("phoneNo")
        formatted_phone_no = validate_phone_no(phone_no)

        user = User.query.filter_by(email=email).first()
        if user:
            flash("User with that email already exists", category="error")
        elif len(email) < 4:
            flash("Invalid email.", category="error")
        elif len(first_name) < 2:
            flash("First name should be more than 1 character.", category="error")
        elif len(last_name) < 2:
            flash("Last name should be more than 1 character.", category="error")
        elif len(phone_no) < 10:
            flash("Phone no should be at least 10 characters.", category="error")
        elif formatted_phone_no == None:
            flash("Phone Number exists", category="error")
        else:
            # add user to database
            new_user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_no=formatted_phone_no,
                is_admin=False,
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Account created!", category="success")
            return redirect(url_for("users.home"))

    return render_template("users/create.html", user=current_user)


def validate_phone_no(phone_no):
    # Extract last 9 digits from the right and remove any non-digit characters
    normalized_phone_no = "".join(filter(str.isdigit, phone_no[-9:]))

    # Check if the normalized phone number already exists in the database
    existing_user = User.query.filter_by(phone_no=normalized_phone_no).first()
    if existing_user:
        # If the phone number already exists, return None (indicating validation failure)
        return None

    # If the phone number is valid and does not already exist, append the country code
    country_code = "+254"
    final_phone_no = country_code + normalized_phone_no
    return final_phone_no


@users.route("/get_user_details/<int:user_id>/", methods=["GET", "POST"])
@login_required
def get_user_details(user_id):
    # Retrieve the user's book order information
    user_orders = Book_Order.query.filter_by(user_id=user_id).all()

    if user_orders:
        order_info_list = []

        for order in user_orders:
            # Calculate lease time
            lease_time = (datetime.now() - order.issue_date).days

            # Calculate fee based on lease time
            if lease_time <= 14:
                fine = 0
            else:
                fine = 0.3 * order.fee * (lease_time - 14)

            total_transaction_amount = order.fee + fine

            # Append relevant information to the result list
            order_info = {
                'user_id': order.user_id,
                'book_title': order.book.title,
                'issue_date': order.issue_date,
                'lease_time': lease_time,
                'total_fine': round(fine, 0),
                'total_charge_fee': order.fee,
                'total_amount': total_transaction_amount
            }

            order_info_list.append(order_info)
            user_orders=order_info_list

        # return order_info_list
            return render_template("users/user_book_orders.html", user_orders=user_orders, user=current_user)
    else:
        flash("User has no book records at this time.", category="error")
        return redirect(url_for('users.home'))