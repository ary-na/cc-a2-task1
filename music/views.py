import boto3
from flask import Blueprint, render_template, redirect, session, url_for, flash

from music.models import QueryForm, Songs

views = Blueprint('views', __name__, template_folder="templates/music")

songs = Songs(boto3.resource('dynamodb', 'ap-southeast-2'))


@views.route('/')
def home():
    if not session.get('email'):
        return redirect(url_for('auth.login'))
    return render_template("index.html")


@views.route('/query', methods=['GET', 'POST'])
def query():
    if not session.get('email'):
        return redirect(url_for('auth.login'))

    form = QueryForm()
    query_songs = []

    if form.validate_on_submit():
        title = form.title.data
        year = form.year.data
        artist = form.artist.data

        if songs.exists("music"):
            if title and not year and not artist:
                query_songs = songs.query_music(title, year, artist)
            elif year and not title and not artist:
                query_songs = songs.query_music(title, year, artist)
            elif artist and not year and not title:
                query_songs = songs.query_music(title, year, artist)
            elif title and year and not artist:
                query_songs = songs.query_music(title, year, artist)
            elif title and artist and not year:
                query_songs = songs.query_music(title, year, artist)
            elif artist and year and not title:
                query_songs = songs.query_music(title, year, artist)
            elif

            query_songs = songs.query_music(title, year, artist)
            if not query_songs:
                flash("No result is retrieved. Please query again.")

            print(query_songs)

    return render_template("query.html", form=form, songs=query_songs)
