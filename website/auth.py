from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.',category='error')
    
    return render_template("admin/login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        phone_no = request.form.get('phoneNo')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

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
        # elif User.validate_phone_no(phone_no) == False:
        #     flash('Phone no exists!', category='error')   
        elif password != confirm_password:
            flash('Passwords do not match!', category='error')
        elif len(password) < 7:
            flash('Password should be more than 6 characters.', category='error')
        else:
            # add user to database
            new_user = User(
                email=email, 
                first_name=first_name, 
                last_name=last_name, 
                phone_no=phone_no,
                is_admin=True,
                password=generate_password_hash(password, method='pbkdf2:sha256')
                )
            db.session.add(new_user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("admin/sign_up.html", user=current_user)

