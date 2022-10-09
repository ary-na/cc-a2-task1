import boto3
from flask import Blueprint, render_template, redirect, session, flash

from music.models import LoginForm, RegisterForm, Logins

music = Blueprint('music', __name__, template_folder="templates/music")

logins = Logins(boto3.resource('dynamodb', 'ap-southeast-2'))


@music.route('/')
def index():
    if not session.get('email'):
        return redirect('/login')
    session.clear()
    return render_template('index.html')


@music.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if logins.exists("login"):
            try:
                account = logins.get_login(email, password)
                if account:
                    session['email'] = account['email']
                    session['user_name'] = account['user_name']
                    return redirect('/')
            except KeyError:
                flash("Email or password is invalid.")

    return render_template('auth/login.html', form=form)


@music.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        return True
    return render_template('auth/register.html', form=form)
