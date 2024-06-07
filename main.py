import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from mongo_jsonschema import SchemaGenerator
from pymongo import MongoClient


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
    schema_dictionary = schema_generator.get_schemas(
        db=database_name,
        collections=[collection_name],
        sample_percent=.99
    )
    logger.info(f'{type(schema_dictionary)=}')
    logger.info('leaving')
    return schema_dictionary


def write_schema_to_file(json_data, external_file_name) -> None:
    logger.info(f'{json_data=}')
    logger.info(f'{Path(external_file_name)=}')
    Path(external_file_name).write_text(json.dumps(json_data, sort_keys=False, indent=4))


def convert_schema_dictionary_to_pyodmongo_dictionary(properties: dict) -> dict:
    retval = {}
    for column_name, type_dictionary in properties.items():
        # logger.info(f'{column_name=} {type_dictionary=}')
        # NOTE: since value is actually a dictionary with a single key, type, unpack it
        column_type_generic: str = type_dictionary['type']
        # logger.info(f'{column_name=} {column_type_generic=}')
        column_type: str = convert_generic_column_type_to_python_type(column_type_generic)
        logger.info(f'{column_name=} {column_type=}')
        retval[column_name] = column_type
    return retval


def convert_generic_column_type_to_python_type(generic_type: str) -> str:
    match generic_type:
        case 'string':
            return 'str'
        case 'integer':
            return 'int'
        case _:
            return 'unknown'


if __name__ == '__main__':
    start_logging()
    logger.info(f'Python version {get_python_version()}')
    logger.info(f'MongoDB Atlas URI: {get_mongodb_atlas_uri()}')

    verify_mongodb_database()

    database_name: str = os.environ.get('mongodb_database_name')
    collection_name: str = os.environ.get('mongodb_collection_name')
    collection_schema_dictionary = get_schema_for_collection(database_name, collection_name)
    logger.info(f'schema: {collection_schema_dictionary}')
    external_filename: str = f'{collection_name}-schema.json'
    properties_dictionary: dict = collection_schema_dictionary[0]['properties']
    write_schema_to_file(properties_dictionary, external_filename)

    class_dictionary: dict = convert_schema_dictionary_to_pyodmongo_dictionary(properties_dictionary)
