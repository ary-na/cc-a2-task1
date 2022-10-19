import boto3
from flask import Blueprint, redirect, session, flash, render_template, url_for
from music.models import Logins, LoginForm, RegisterForm

# [21] "What is Python KeyError and How to Handle it with 3 Examples", A-Z Tech, 2022. [Online]. Available:
# https://www.jquery-az.com/python-keyerror-handle-3-examples/. [Accessed: 19- Oct- 2022].
#
# [22] C. Hansen, "Python KeyError Exceptions and How to Handle Them – Real Python", Realpython.com, 2022. [Online].
# Available: https://realpython.com/python-keyerror/. [Accessed: 19- Oct- 2022].


auth = Blueprint('auth', __name__, template_folder="templates/music")

logins = Logins(boto3.resource('dynamodb', 'ap-southeast-2'))


# Login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if logins.exists("login"):
            try:
                user = logins.get_login(email)
                if user and user['password'] == password:
                    session['email'] = user['email']
                    session['user_name'] = user['user_name']
                    return redirect(url_for("views.home"))
            except KeyError:
                flash("Email or password is invalid.")

    return render_template('auth/login.html', form=form)


# Register
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        user_name = form.user_name.data
        password = form.password.data

        if logins.exists("login"):
            email_exists = logins.query_login(email)
            if email_exists:
                flash("The email already exists.")
            else:
                logins.add_login(email, user_name, password)
                return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


# Logout
@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
