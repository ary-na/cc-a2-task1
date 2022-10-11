from flask import Blueprint, render_template, redirect, session, url_for

views = Blueprint('views', __name__, template_folder="templates/music")


@views.route('/')
def home():
    if not session.get('email'):
        return redirect(url_for('auth.login'))
    return render_template("index.html")
