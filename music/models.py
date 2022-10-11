import json
import logging
import requests
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired

logger = logging.getLogger(__name__)


class Logins:
    def __init__(self, dyn_resource):
        self.dyn_resource = dyn_resource
        self.table = None

    def exists(self, table_name):
        try:
            table = self.dyn_resource.Table(table_name)
            table.load()
            exists = True
        except ClientError as err:
            if err.response['Error']['Code'] == 'ResourceNotFoundException':
                exists = False
            else:
                logger.error(
                    "Couldn't check for existence of %s. Here's why: %s: %s",
                    table_name,
                    err.response['Error']['Code'], err.response['Error']['Message'])
                raise
        else:
            self.table = table
        return exists

    def create_table(self, table_name):
        try:
            self.table = self.dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'email', 'KeyType': 'HASH'},  # Partition key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'email', 'AttributeType': 'S'},
                ],
                ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10})
            self.table.wait_until_exists()
        except ClientError as err:
            logger.error(
                "Couldn't create table %s. Here's why: %s: %s", table_name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return self.table

    def write_batch(self, logins):
        try:
            with self.table.batch_writer() as writer:
                for login in logins:
                    writer.put_item(Item=login)
        except ClientError as err:
            logger.error(
                "Couldn't load data into table %s. Here's why: %s: %s", self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise

    def get_login(self, email):
        try:
            response = self.table.get_item(Key={'email': email})
        except ClientError as err:
            logger.error(
                "Couldn't get movie %s from table %s. Here's why: %s: %s",
                email, self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response['Item']

    def add_login(self, email, password, user_name):
        try:
            self.table.put_item(
                Item={
                    'email': email,
                    'password': password,
                    'user_name': user_name})
        except ClientError as err:
            logger.error(
                "Couldn't add login %s to table %s. Here's why: %s: %s",
                email, self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise

    def query_login(self, email):
        try:
            response = self.table.query(KeyConditionExpression=Key('email').eq(email))
        except ClientError as err:
            logger.error(
                "Couldn't query for login with email %s. Here's why: %s: %s", email,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response['Items']


class Songs:
    def __init__(self, dyn_resource):
        self.table = None
        self.dyn_resource = dyn_resource

    def exists(self, table_name):
        try:
            table = self.dyn_resource.Table(table_name)
            table.load()
            exists = True
        except ClientError as err:
            if err.response['Error']['Code'] == 'ResourceNotFoundException':
                exists = False
            else:
                logger.error(
                    "Couldn't check for existence of %s. Here's why: %s: %s",
                    table_name,
                    err.response['Error']['Code'], err.response['Error']['Message'])
                raise
        else:
            self.table = table
        return exists

    def create_table(self, table_name):
        try:
            self.table = self.dyn_resource.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'title', 'KeyType': 'HASH'},  # Partition key
                    {'AttributeName': 'artist', 'KeyType': 'RANGE'},  # Sort key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'title', 'AttributeType': 'S'},
                    {'AttributeName': 'artist', 'AttributeType': 'S'},
                ],
                ProvisionedThroughput={'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10})
            self.table.wait_until_exists()
        except ClientError as err:
            logger.error(
                "Couldn't create table %s. Here's why: %s: %s", table_name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return self.table

    def write_batch(self, songs):
        try:
            with self.table.batch_writer() as writer:
                for song in songs:
                    writer.put_item(Item=song)
        except ClientError as err:
            logger.error(
                "Couldn't load data into table %s. Here's why: %s: %s", self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise

    def scan_images(self):
        try:
            response = self.table.scan(AttributesToGet=['img_url'])
        except ClientError as err:
            logger.error(
                "Couldn't query for img_url %s. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response['Items']


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired()])
    user_name = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Register')


def get_login_data(logins_file_name):
    try:
        with open(logins_file_name) as login_file:
            login_data = json.load(login_file)
    except FileNotFoundError:
        print(f"File {logins_file_name} not found.")
        raise
    else:
        return login_data


def get_song_data(songs_file_name):
    try:
        with open(songs_file_name) as song_file:
            song_data = json.load(song_file)
    except FileNotFoundError:
        print(f"File {songs_file_name} not found.")
        raise
    else:
        return song_data


def init_logins(table_name, logins_file_name, dyn_resource):
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    print('-' * 88)
    print("Initializing logins.")
    print('-' * 88)

    logins = Logins(dyn_resource)
    logins_exists = logins.exists(table_name)
    if not logins_exists:
        print(f"\nCreating table {table_name}...")
        logins.create_table(table_name)
        print(f"\nCreated table {logins.table.name}.")

        login_data = get_login_data(logins_file_name)
        print(f"\nReading data from '{logins_file_name}' into your table.")
        logins.write_batch(login_data)
        print(f"\nWrote {len(logins_file_name)} logins into {logins.table.name}.")

    return logins


def init_songs(table_name, songs_file_name, dyn_resource):
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    print('-' * 88)
    print("Initializing songs.")
    print('-' * 88)

    songs = Songs(dyn_resource)
    songs_exists = songs.exists(table_name)
    if not songs_exists:
        print(f"\nCreating table {table_name}...")
        songs.create_table(table_name)
        print(f"\nCreated table {songs.table.name}.")

        song_data = get_song_data(songs_file_name)
        print(f"\nReading data from '{songs_file_name}' into your table.")
        songs.write_batch(song_data)
        print(f"\nWrote {len(songs_file_name)} songs into {songs.table.name}.")

    return songs


def get_images(table_name, dyn_resource, s3_client):
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    print('-' * 88)
    print("Uploading images.")
    print('-' * 88)

    bucket_name = "cc-a2-task1-img"

    if get_num_objs(bucket_name, s3_client) == 0:
        songs = Songs(dyn_resource)
        songs_exists = songs.exists(table_name)
        if songs_exists:
            images = songs.scan_images()
            if images:
                print(f"There were {len(images)}:")
                for image in images:
                    upload_image(image['img_url'], bucket_name, s3_client)
            else:
                print("I don't know about any images!")


def upload_image(url, bucket_name, s3_client, object_name=None):
    if object_name is None:
        object_name = url

    try:
        response = requests.get(url, stream=True)
        s3_client.upload_fileobj(response.raw, bucket_name, object_name)
    except ClientError as err:
        logger.error(err)
        return False

    return True


def get_num_objs(bucket, s3_client):
    num_objs = 0

    paginator = s3_client.get_paginator("list_objects_v2")
    for res in paginator.paginate(
            Bucket=bucket,
    ):
        if "Contents" not in res:
            print(f"""No contents in res={res}""")
            continue
        num_objs += len(res["Contents"])

    return num_objs


def generate_pre_signed_url(s3_client, client_method, method_parameters, expires_in):
    try:
        url = s3_client.generate_presigned_url(
            ClientMethod=client_method,
            Params=method_parameters,
            ExpiresIn=expires_in
        )
        logger.info("Got presigned URL: %s", url)
    except ClientError:
        logger.exception(
            "Couldn't get a presigned URL for client method '%s'.", client_method)
        raise
    return url
