import boto3
from flask import Blueprint, render_template, redirect, session, url_for, flash

from music.models import QueryForm, Songs, generate_pre_signed_url, subscribe_new_music, Subscriptions, remove_music

views = Blueprint('views', __name__, template_folder="templates/music")

songs = Songs(boto3.resource('dynamodb', 'ap-southeast-2'))
subscriptions = Subscriptions(boto3.resource('dynamodb', 'ap-southeast-2'))


@views.route('/')
def home():
    if not session.get('email'):
        return redirect(url_for('auth.login'))

    scan_subscriptions = {}
    if subscriptions.exists("subscriptions"):
        scan_subscriptions = subscriptions.scan_subscriptions()

    return render_template("index.html", subscriptions=scan_subscriptions,
                           generate_pre_signed_url=generate_pre_signed_url)


@views.route('/query', methods=['GET', 'POST'])
def query():
    if not session.get('email'):
        return redirect(url_for('auth.login'))

    form = QueryForm()
    scan_songs = {}

    if form.validate_on_submit():
        title = form.title.data
        year = form.year.data
        artist = form.artist.data

        if songs.exists("music"):
            scan_songs = songs.scan_songs(title, year, artist)
            if not scan_songs:
                flash("No result is retrieved. Please query again.")

    return render_template("query.html", form=form, songs=scan_songs, generate_pre_signed_url=generate_pre_signed_url)


@views.route('/subscribe/<title>/<artist>')
def subscribe(title, artist):
    subscribe_new_music(title, artist)
    return redirect(url_for('views.home'))


@views.route('/remove/<title>')
def remove(title):
    remove_music(session['email'], title)
    return redirect(url_for('views.home'))
