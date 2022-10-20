import json
import logging

import boto3
import requests
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from flask import session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired

# [1] K. Huiyeon, "Step-by-step visual guide on deploying a Flask application on AWS EC2", Medium, 2022. [Online].
# Available: https://medium.com/techfront/step-by-step-visual-guide-on-deploying-a-flask-application-on-aws-ec2
# -8e3e8b82c4f7. [Accessed: 07- Oct- 2022].
#
# [2] harshsethi2000, "How to Install Python3 on AWS EC2? - GeeksforGeeks", GeeksforGeeks, 2022. [Online]. Available:
# https://www.geeksforgeeks.org/how-to-install-python3-on-aws-ec2/. [Accessed: 07- Oct- 2022].
#
# [3] "How to Use Nano, the Linux Command Line Text Editor", linuxize, 2022. [Online]. Available:
# https://linuxize.com/post/how-to-use-nano-text-editor/. [Accessed: 07- Oct- 2022].
#
# [4] B. Rhodes, "How to leave/exit/deactivate a Python virtualenv", Stack Overflow, 2022. [Online]. Available:
# https://stackoverflow.com/questions/990754/how-to-leave-exit-deactivate-a-python-virtualenv. [Accessed: 07- Oct-
# 2022].
#
# [5] "Deploying a Django application to Elastic Beanstalk", docs.aws.amazon.com, 2022. [Online]. Available:
# https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-django.html. [Accessed: 07- Oct- 2022].
#
# [6] "Ubuntu Manpage: networkd-dispatcher - Dispatcher service for systemd-networkd connection status changes",
# Manpages.ubuntu.com, 2022. [Online]. Available:
# https://manpages.ubuntu.com/manpages/kinetic/man8/networkd-dispatcher.8.html. [Accessed: 07- Oct- 2022].
#
# [7] R. Gupta, "How to deploy Python Django Project on AWS EC2 Ubuntu Server.", Medium, 2022. [Online]. Available:
# https://medium.com/nerd-for-tech/how-to-deploy-python-django-project-on-aws-ec2-ubuntu-server-5c484fdb8f8c. [
# Accessed: 07- Oct- 2022].
#
# [8] "Error connecting to your instance: Connection timed out", docs.aws.amazon.com/, 2022. [Online]. Available:
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/TroubleshootingInstancesConnecting.html
# #TroubleshootingInstancesConnectionTimeout. [Accessed: 07- Oct- 2022].
#
# [9] "Associate a static public IP address with your EC2 instance", Amazon Web Services, Inc., 2022. [Online].
# Available: https://aws.amazon.com/premiumsupport/knowledge-center/ec2-associate-static-public-ip/. [Accessed: 07-
# Oct- 2022].
#
# [10] R. Chakrabarty, J. Rotenstein and R. Chakrabarty, "I cannot SSH to my Linux EC2 Instance from My IP suggested
# by AWS. It works if incoming rule is set to ::0", Stack Overflow, 2022. [Online]. Available:
# https://stackoverflow.com/questions/66650254/i-cannot-ssh-to-my-linux-ec2-instance-from-my-ip-suggested-by-aws-it
# -works-if-i. [Accessed: 07- Oct- 2022].
#
# [11] "Amazon EC2 instance IP addressing", docs.aws.amazon.com/, 2022. [Online]. Available:
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-instance-addressing.html#using-instance-addressing-common
# . [Accessed: 07- Oct- 2022].
#
# [12] "Resolve "Connection refused" or "Connection timed out" Errors When Connecting to an EC2 Instance with SSH",
# Amazon Web Services, Inc., 2022. [Online]. Available:
# https://aws.amazon.com/premiumsupport/knowledge-center/ec2-linux-resolve-ssh-connection-errors/. [Accessed: 07-
# Oct- 2022].
#
# [13] N. Hadiq, "Deploy a Flask app on AWS EC2", Medium, 2022. [Online]. Available:
# https://medium.com/innovation-incubator/deploy-a-flask-app-on-aws-ec2-d1d774c275a2. [Accessed: 07- Oct- 2022].
#
#
# [23] S. S, "CRUD operations on DynamoDB with Flask APIs", Medium, 2022. [Online]. Available:
# https://medium.com/featurepreneur/crud-operations-on-dynamodb-with-flask-apis-916f6cae992. [Accessed: 19- Oct- 2022].
#
# [24] B. Oakley and Blendouble, "NoneType' object has no attribute '__getitem__'", Stack Overflow, 2022. [Online].
# Available: https://stackoverflow.com/questions/24119731/nonetype-object-has-no-attribute-getitem. [Accessed: 19-
# Oct- 2022].
#
# [25] Laren-AWS, "aws-doc-sdk-examples/scenario_getting_started_movies.py at main · awsdocs/aws-doc-sdk-examples",
# GitHub, 2022. [Online]. Available: https://github.com/awsdocs/aws-doc-sdk-examples/blob/main/python/example_code
# /dynamodb/GettingStarted/scenario_getting_started_movies.py. [Accessed: 19- Oct- 2022].
#
# [26] Tech With Tim, "Python Website Full Tutorial - Flask, Authentication, Databases & More", Youtube.com,
# 2022. [Online]. Available: https://www.youtube.com/watch?v=dam0GPOAvVI&t=7143s. [Accessed: 19- Oct- 2022].
#
# [27] J. Rai, "Upload Files To S3 in Python using boto3 | Python Upload Files to S3 - TutorialsBuddy",
# Tutorialsbuddy.com, 2022. [Online]. Available: https://www.tutorialsbuddy.com/python-upload-file-to-s3. [Accessed:
# 19- Oct- 2022].
#
# [28] J. Rotenstein, D. Richard and Z. Smith, "How to determine if an AWS s3 bucket has at least one public
# object?", Stack Overflow, 2022. [Online]. Available:
# https://stackoverflow.com/questions/61066179/how-to-determine-if-an-aws-s3-bucket-has-at-least-one-public-object. [
# Accessed: 19- Oct- 2022].
#
# [29] ampersand, Quentin, ALFA and Lê Tư Thành, "How to query all rows of one column in DynamoDB?", Stack Overflow,
# 2022. [Online]. Available: https://stackoverflow.com/questions/54996861/how-to-query-all-rows-of-one-column-in
# -dynamodb. [Accessed: 19- Oct- 2022].
#
# [30] B. Solomon and MP32, ""No connection adapters were found"", Stack Overflow, 2022. [Online]. Available:
# https://stackoverflow.com/questions/72192980/no-connection-adapters-were-found. [Accessed: 19- Oct- 2022].
#
# [31] "presigned_url.py", docs.aws.amazon.com, 2022. [Online]. Available:
# https://docs.aws.amazon.com/code-samples/latest/catalog/python-s3-s3_basics-presigned_url.py.html. [Accessed: 19-
# Oct- 2022].
#
# [32] "How to convert a dictionary to a string in Python? - AskPython", AskPython, 2022. [Online]. Available:
# https://www.askpython.com/python/string/dictionary-to-a-string. [Accessed: 19- Oct- 2022].
#
# [33] dgh et al., "Upload image available at public URL to S3 using boto", Stack Overflow, 2022. [Online].
# Available: https://stackoverflow.com/questions/14346065/upload-image-available-at-public-url-to-s3-using-boto?rq=1.
# [Accessed: 19- Oct- 2022].
#
# [34] A. Yohan Malshika, "DynamoDB Filter Expressions (Ultimate Guide w/ Examples)", Dynobase.dev, 2022. [Online].
# Available: https://dynobase.dev/dynamodb-filterexpression/. [Accessed: 19- Oct- 2022].
#
# [35] P. Acsany, "Primer on Jinja Templating – Real Python", Realpython.com, 2022. [Online]. Available:
# https://realpython.com/primer-on-jinja-templating/. [Accessed: 19- Oct- 2022].
#
# [36] "Write an item to a DynamoDB table", docs.aws.amazon.com, 2022. [Online]. Available:
# https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.WriteItem.html. [Accessed: 19- Oct-
# 2022].
#
# [37] Laren-AWS, "aws-doc-sdk-examples/scenario_getting_started_movies.py at main · awsdocs/aws-doc-sdk-examples",
# GitHub, 2022. [Online]. Available: https://github.com/awsdocs/aws-doc-sdk-examples/blob/main/python/example_code
# /dynamodb/GettingStarted/scenario_getting_started_movies.py. [Accessed: 19- Oct- 2022].


# [38] L. Stanley, R. Cowie, Никита Шишкин and gerardw, "Call a python function from jinja2", Stack Overflow,
# 2022. [Online]. Available: https://stackoverflow.com/questions/6036082/call-a-python-function-from-jinja2. [
# Accessed: 19- Oct- 2022].
#
# [39] "QueryFilter", docs.aws.amazon.com, 2022. [Online]. Available:
# https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/LegacyConditionalParameters.QueryFilter.html. [
# Accessed: 19- Oct- 2022].
#
# [40] "Scan a DynamoDB table", docs.aws.amazon.com, 2022. [Online]. Available:
# https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Scan.html. [Accessed: 19- Oct- 2022].
#
# [41] "Python Switch Case with Examples", pythongeeks.org, 2022. [Online]. Available:
# https://pythongeeks.org/switch-in-python/. [Accessed: 19- Oct- 2022].
#
# [42] T. Lathuille et al., "Dynamodb scan() using FilterExpression", Stack Overflow, 2022. [Online]. Available:
# https://stackoverflow.com/questions/44704443/dynamodb-scan-using-filterexpression. [Accessed: 19- Oct- 2022].
#
# [43] "Query a DynamoDB table", docs.aws.amazon.com, 2022. [Online]. Available:
# https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GettingStarted.Query.html. [Accessed: 19- Oct-
# 2022].
#
# [44] J. Astrahan, P. Sharma, D. Grinko, marc_s, Kevin Hooke and Eyal Ch, "How do I query DynamoDB with non primary
# key field?", Stack Overflow, 2022. [Online]. Available:
# https://stackoverflow.com/questions/47569793/how-do-i-query-dynamodb-with-non-primary-key-field. [Accessed: 19-
# Oct- 2022].

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

    def add_login(self, email, user_name, password):
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

    def get_song(self, title, artist):
        try:
            response = self.table.get_item(Key={'title': title, 'artist': artist})
        except ClientError as err:
            logger.error(
                "Couldn't get song %s from table %s. Here's why: %s: %s",
                title, self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response['Item']

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

    def scan_songs(self, title, year, artist):

        if title:
            filter_expression = Attr('title').eq(title)
        elif year:
            filter_expression = Attr('year').eq(year)
        elif artist:
            filter_expression = Attr('artist').eq(artist)
        elif title and year:
            filter_expression = Attr('title').eq(title) & Attr('year').eq(year)
        elif title and artist:
            filter_expression = Attr('title').eq(title) & Attr('artist').eq(artist)
        elif year and artist:
            filter_expression = Attr('year').eq(year) & Attr('artist').eq(artist)
        else:
            filter_expression = Attr('title').eq(title) & Attr('year').eq(year) & Attr('artist').eq(artist)

        try:
            response = self.table.scan(FilterExpression=filter_expression)
        except ClientError as err:
            logger.error(
                "Couldn't query for songs %s. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response['Items']


class Subscriptions:
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
                    {'AttributeName': 'email', 'KeyType': 'HASH'},  # Partition key
                    {'AttributeName': 'title', 'KeyType': 'RANGE'}  # Sort key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'email', 'AttributeType': 'S'},
                    {'AttributeName': 'title', 'AttributeType': 'S'},
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

    def add_song(self, email, song):
        try:
            self.table.put_item(
                Item={
                    'email': email,
                    'title': song['title'],
                    'song': {'title': song['title'], 'artist': song['artist'], 'year': song['year'],
                             'web_url': song['web_url'], 'img_url': song['img_url']}})
        except ClientError as err:
            logger.error(
                "Couldn't add movie %s to table %s. Here's why: %s: %s",
                email, self.table.name,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise

    def scan_subscriptions(self):
        try:
            response = self.table.scan(FilterExpression=Attr('email').eq(session['email']))
        except ClientError as err:
            logger.error(
                "Couldn't query for songs %s. Here's why: %s: %s",
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise
        else:
            return response['Items']

    def delete_song(self, email, title):
        try:
            self.table.delete_item(Key={'email': email, 'title': title})
        except ClientError as err:
            logger.error(
                "Couldn't delete movie %s. Here's why: %s: %s", title,
                err.response['Error']['Code'], err.response['Error']['Message'])
            raise


songs = Songs(boto3.resource('dynamodb', 'ap-southeast-2'))
subscriptions = Subscriptions(boto3.resource('dynamodb', 'ap-southeast-2'))


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired()])
    user_name = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Register')


class QueryForm(FlaskForm):
    title = StringField('Title')
    year = StringField('Year')
    artist = StringField('Artist')
    submit = SubmitField('Query')


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


def init_subscriptions(table_name, dyn_resource):
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    print('-' * 88)
    print("Initializing subscriptions.")
    print('-' * 88)

    subscriptions = Subscriptions(dyn_resource)
    subscriptions_exists = subscriptions.exists(table_name)

    if not subscriptions_exists:
        print(f"\nCreating table {table_name}...")
        subscriptions.create_table(table_name)
        print(f"\nCreated table {subscriptions.table.name}.")

    return subscriptions


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


def generate_pre_signed_url(s3_object_key):
    s3_client = boto3.client('s3')
    try:
        url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={'Bucket': "cc-a2-task1-img", 'Key': s3_object_key},
            ExpiresIn=3600
        )
        logger.info("Got pre-signed URL: %s", url)
    except ClientError:
        logger.exception(
            "Couldn't get a pre-signed URL for client method '%s'.")
        raise
    return url


def subscribe_new_music(partition_key, sort_key):
    song = {}
    if songs.exists("music"):
        song = songs.get_song(partition_key, sort_key)

    if subscriptions.exists("subscriptions"):
        subscriptions.add_song(session['email'], song)


def remove_music(partition_key, sort_key):
    if subscriptions.exists("subscriptions"):
        subscriptions.delete_song(partition_key, sort_key)
