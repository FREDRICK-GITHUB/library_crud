from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import Transaction, User
from flask_login import login_required, current_user
from . import db
from sqlalchemy.sql import func


transactions = Blueprint("transactions", __name__)


@transactions.route("/transactions", methods=["GET", "POST"])
@login_required
def view_transactions():
    transactions = Transaction.query.all()
    return render_template(
        "/transactions/transactions.html", transactions=transactions, user=current_user
    )


@transactions.route("/create_new_transaction", methods=["GET", "POST"])
@login_required
def create_new_transaction():
    users = User.query.all()

    if request.method == "POST":
        amount = request.form.get("amount")
        date = func.now().strftime('%Y-%m-%d %H:%M:%S')
        user_id = request.form.get("user_id")
        user = User.query.filter_by(id=user_id).first()

        if int(amount) < 1:
            flash("Amount must be more than 1.", category="error")
        elif user == None:
            flash("Inaccurate user information!", category="error")
        else:
            new_transaction = Transaction(amount=amount, date=date, user_id=user_id)
            db.session.add(new_transaction)
            db.session.commit()
            flash("New transaction added!", category="success")
            return redirect(url_for("transactions.view_transactions"))

    return render_template("/transactions/create.html", users=users, user=current_user)
