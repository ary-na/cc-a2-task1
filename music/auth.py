import boto3
from flask import Blueprint, redirect, session, flash, render_template, url_for
from music.models import Logins, LoginForm, RegisterForm

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
