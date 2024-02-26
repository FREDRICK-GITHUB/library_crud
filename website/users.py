from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User
from flask_login import  login_required, current_user
from . import db
import json

users = Blueprint('users', __name__)


@users.route('/view_users', methods=['GET', 'POST'])
@login_required
def home():
    # return jsonify({})
    members = User.query.all()
    return render_template("users/read.html", members=members, user=current_user)



@users.route('/create_new_user', methods=['GET', 'POST'])
@login_required
def createNewUser():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        phone_no = request.form.get('phoneNo')
        formatted_phone_no = validate_phone_no(phone_no)
        
        user = User.query.filter_by(email=email).first()
        if user:
            flash('User with that email already exists', category='error')
        elif len(email) < 4:
            flash('Invalid email.', category='error')
        elif len(first_name) < 2:
            flash('First name should be more than 1 character.', category='error')
        elif len(last_name) < 2:
            flash('Last name should be more than 1 character.', category='error')
        elif len(phone_no) < 10:
            flash('Phone no should be at least 10 characters.', category='error')
        elif formatted_phone_no == None:
            flash('Phone Number exists', category='error')
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
            flash('Account created!', category='success')
            return redirect(url_for('users.home'))
 
    return render_template("users/create.html", user=current_user)



def validate_phone_no(phone_no):
    # Extract last 9 digits from the right and remove any non-digit characters
    normalized_phone_no = ''.join(filter(str.isdigit, phone_no[-9:]))

    # Check if the normalized phone number already exists in the database
    existing_user = User.query.filter_by(phone_no=normalized_phone_no).first()
    if existing_user:
        # If the phone number already exists, return None (indicating validation failure)
        return None

    # If the phone number is valid and does not already exist, append the country code
    country_code = '+254'
    final_phone_no = country_code + normalized_phone_no
    return final_phone_no


