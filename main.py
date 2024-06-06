import os
import sys

from dotenv import load_dotenv
from loguru import logger

from pymongo import MongoClient
from pyodmongo import DbEngine
from pyodmongo.queries import eq

from mongo_jsonschema import SchemaGenerator


def get_python_version() -> str:
    return f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'


def get_mongodb_atlas_uri() -> str:
    load_dotenv()

    template: str = os.environ.get('mongodb_connection_template')
    uid: str = os.environ.get('mongodb_uid')
    pwd: str = os.environ.get('mongodb_pwd')

    return f'mongodb+srv://{uid}:{pwd}@{template}'


def get_mongodb_client() -> MongoClient:
    # print(f'{get_connection_string()=}')
    return MongoClient(get_mongodb_atlas_uri())


def get_mongodb_database(client: MongoClient, database_name: str):
    return client.get_database(name=database_name)


def get_mongodb_collection(database, collection_name: str):
    return database.get_collection(collection_name)


def start_logging():
    log_format: str = '{time} - {name} - {level} - {function} - {message}'
    logger.remove()
    logger.add('formatted_log.txt', format=log_format, rotation='10 MB', retention='5 days')


def verify_mongodb_database():
    logger.info('top')
    client: MongoClient = get_mongodb_client()
    logger.info(f'{client=}')
    database_name: str = os.environ.get('mongodb_database_name')
    print(f'{database_name=}')
    db = get_mongodb_database(client, database_name)
    print(f'{db=}')

    collection_name: str = os.environ.get('mongodb_collection_name')

    products_collection = get_mongodb_collection(db, collection_name)
    print(f'{products_collection=}')
    logger.info('leaving')


def get_schema_for_collection(database_name: str, collection_name: str) -> str:
    logger.info('top')
    client: MongoClient = get_mongodb_client()
    db = get_mongodb_database(client, database_name)
    collection = get_mongodb_collection(db, collection_name)

    uri = get_mongodb_atlas_uri()
    schema_generator = SchemaGenerator(uri)
    schema2 = schema_generator.get_schemas(
        db=database_name,
        collections=[collection_name],
        sample_percent=.99
    )
    logger.info(f'{type(schema2)=}')
    # dicitionary:
    # $schema: str = 'http://json-schema.org/schema#
    # type: str = 'object'
    # properties : dictionary
    #   _id: string
    #   category: string
    #   id_visible: integer
    #   image: string
    #   name: string
    #  price: integer
    # required: list
    #   _id : str
    #   _category : str
    #   id_visible : str
    #   image : str
    #   name : str
    #   price: str
    logger.info('leaving')
    return schema2


if __name__ == '__main__':
    start_logging()
    logger.info(f'Python version {get_python_version()}')
    logger.info(f'MongoDB Atlas URI: {get_mongodb_atlas_uri()}')

    verify_mongodb_database()

    database_name: str = os.environ.get('mongodb_database_name')
    collection_name: str = os.environ.get('mongodb_collection_name')
    json_schema = get_schema_for_collection(database_name, collection_name)
    logger.info(f'schema: {json_schema}')
