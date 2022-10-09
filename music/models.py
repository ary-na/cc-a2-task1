import json
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class Logins:
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
                    {'AttributeName': 'user_name', 'KeyType': 'RANGE'},  # Sort key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'email', 'AttributeType': 'S'},
                    {'AttributeName': 'user_name', 'AttributeType': 'S'},
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
