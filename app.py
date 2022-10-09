import boto3
from flask import Flask

from music.models import init_logins, init_songs
# blueprint import
from music.views import music

app = Flask(__name__)

# setup with the configuration provided
app.config.from_object('config.DevelopmentConfig')

# setup all our dependencies
try:
    logins = init_logins('login', 'logins.json', boto3.resource('dynamodb', 'ap-southeast-2'))
    songs = init_songs('music', 'songs.json', boto3.resource('dynamodb', 'ap-southeast-2'))
except Exception as e:
    print(f"Something went wrong with the demo! Here's what: {e}")

# register blueprint
app.register_blueprint(music)

if __name__ == '__main__':
    app.run()
