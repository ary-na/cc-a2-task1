import boto3
from flask import Blueprint, render_template, redirect, session, url_for, flash

from music.models import QueryForm, Songs, generate_pre_signed_url, subscribe_new_music, Subscriptions, remove_music

# [14] "Templates — Flask Documentation (2.2.x)", Flask.palletsprojects.com, 2022. [Online]. Available:
# https://flask.palletsprojects.com/en/2.2.x/templating/#standard-filters. [Accessed: 19- Oct- 2022].
#
# [15] "Flask-Session — Flask-Sessions 0.0.4 documentation", Flask-session.readthedocs.io, 2022. [Online]. Available:
# https://flask-session.readthedocs.io/en/latest/. [Accessed: 19- Oct- 2022].
#
# [16] F. Florencio Garcia, "Flask Sessions, what are they for, how it works, what options I have to persist this
# data?", Medium, 2022. [Online]. Available: https://medium.com/thedevproject/flask-sessions-what-are-they-for-how-it
# -works-what-options-i-have-to-persist-this-data-4ca48a34d3. [Accessed: 19- Oct- 2022].
#
# [17] "Create a DynamoDB table using an AWS SDK", docs.aws.amazon.com, 2022. [Online]. Available:
# https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/example_dynamodb_CreateTable_section.html. [
# Accessed: 19- Oct- 2022].
#
# [18] "How to create JSON File?", Codebeautify.org, 2022. [Online]. Available:
# https://codebeautify.org/blog/how-to-create-json-file/. [Accessed: 19- Oct- 2022].
#
# [19] K. Chris, "CSS Vertical Align – How to Center a Div, Text, or an Image [Example Code]", freeCodeCamp.org,
# 2022. [Online]. Available: https://www.freecodecamp.org/news/css-vertical-align-how-to-center-a-div-text-or-an
# -image-example-code/. [Accessed: 19- Oct- 2022].
#
# [20] a. Mark Otto, "Introduction", Getbootstrap.com, 2022. [Online]. Available:
# https://getbootstrap.com/docs/5.0/getting-started/introduction/. [Accessed: 19- Oct- 2022].
#
# [21] "What is Python KeyError and How to Handle it with 3 Examples", A-Z Tech, 2022. [Online]. Available:
# https://www.jquery-az.com/python-keyerror-handle-3-examples/. [Accessed: 19- Oct- 2022].
#
# [22] C. Hansen, "Python KeyError Exceptions and How to Handle Them – Real Python", Realpython.com, 2022. [Online].
# Available: https://realpython.com/python-keyerror/. [Accessed: 19- Oct- 2022].



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
