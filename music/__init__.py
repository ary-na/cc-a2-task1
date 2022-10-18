import boto3
from flask import Flask
from music.models import init_logins, init_songs, get_images, init_subscriptions


def create_app():
    app = Flask(__name__)

    # setup with the configuration provided
    app.config.from_object('config.DevelopmentConfig')

    # setup all our dependencies
    try:
        init_logins('login', 'logins.json', boto3.resource('dynamodb', 'ap-southeast-2'))
        init_songs('music', 'songs.json', boto3.resource('dynamodb', 'ap-southeast-2'))
        init_subscriptions('subscriptions', boto3.resource('dynamodb', 'ap-southeast-2'))
        get_images('music', boto3.resource('dynamodb', 'ap-southeast-2'), boto3.client('s3'))
    except Exception as e:
        print(f"Something went wrong with the demo! Here's what: {e}")

    # blueprint import
    from .auth import auth
    from .views import views

    # register blueprint
    app.register_blueprint(auth)
    app.register_blueprint(views)

    return app
