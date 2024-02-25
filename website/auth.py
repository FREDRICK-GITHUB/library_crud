from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    data = request.form
    print(data)
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return "<p>Logout</p>"

@auth.route('sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password = request.form.get('password')
        confirmPassword = request.form.get('confirmPassword')

        if len(email) < 4:
            flash('Invalid email.', category='error')
        elif len(firstName) < 2:
            flash('First name should be more than 1 character.', category='error')
        elif len(lastName) < 2:
            flash('Last name should be more than 1 character.', category='error')
        elif password != confirmPassword:
            flash('Passwords do not match!', category='error')
        elif len(password) < 7:
            flash('Password should be more than 6 characters.', category='error')
        else:
            # add user to database
            flash('Account created!', category='success')

    return render_template("sign_up.html")

