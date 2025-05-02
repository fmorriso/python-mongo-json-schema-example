import json
import sys
from importlib.metadata import version
from pathlib import Path

from loguru import logger
# from mongo_jsonschema import SchemaGenerator
from pymongo import MongoClient
from sqlalchemy.sql.ddl import SchemaGenerator

from program_settings import ProgramSettings


def get_python_version() -> str:
    return f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'


def get_package_version(package_name: str) -> str:
    return version(package_name)


def get_mongodb_atlas_uri() -> str:
    template: str = ProgramSettings.get_setting('MONGODB_CONNECTION_TEMPLATE')
    uid: str = ProgramSettings.get_setting('MONGODB_UID')
    pwd: str = ProgramSettings.get_setting('MONGODB_PWD')

    return f'mongodb+srv://{uid}:{pwd}@{template}'


def get_mongodb_client() -> MongoClient:
    # print(f'{get_connection_string()=}')
    return MongoClient(get_mongodb_atlas_uri())


def get_mongodb_database(client: MongoClient, database_name: str):
    return client.get_database(name = database_name)


def get_mongodb_collection(database, collection_name: str):
    return database.get_collection(collection_name)


def start_logging():
    log_format: str = '{time} - {name} - {level} - {function} - {message}'
    logger.remove()
    logger.add('formatted_log.txt', format = log_format, rotation = '10 MB', retention = '5 days')
    # Add a handler that logs only DEBUG messages to stdout
    logger.add(sys.stdout, level = 'DEBUG', filter = lambda record: record["level"].name == "DEBUG")


def verify_mongodb_database():
    logger.info('top')
    client: MongoClient = get_mongodb_client()
    logger.info(f'{client=}')
    database_name: str = ProgramSettings.get_setting('mongodb_database_name')
    print(f'{database_name=}')
    db = get_mongodb_database(client, database_name)
    print(f'{db=}')

    collection_name: str = ProgramSettings.get_setting('mongodb_collection_name')

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
        db = database_name,
        collections = [collection_name],
        sample_percent = .99
    )
    logger.info(f'{type(schema_dictionary)=}')
    logger.info('leaving')
    return schema_dictionary


def write_schema_to_file(json_data, external_file_name) -> None:
    logger.info(f'{json_data=}')
    logger.info(f'{Path(external_file_name)=}')
    Path(external_file_name).write_text(json.dumps(json_data, sort_keys = False, indent = 4))


def convert_schema_dictionary_to_pyodmongo_dictionary(properties: dict) -> dict:
    retval = {}
    for column_name, type_dictionary in properties.items():
        # logger.info(f'{column_name=} {type_dictionary=}')

        # NOTE: since MongoDB automatically accounts for the built-in _id column, don't include it
        #       in the output dictionary
        if column_name == '_id':
            continue

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


def write_pyodmongo_class(db_name: str, class_name: str, fields: dict):
    """write a python class file using the supplied class name and dictionary of fields."""
    # NOTE: the class name is expected to have a leading capital letter
    logger.info(f'Begin class {class_name}')
    class_filename: str = f'{class_name.lower()}.py'
    standard_header_stuff: str = f'from typing import ClassVar\n\nfrom pyodmongo import DbModel\n\n\n'
    indent: str = ' ' * 4
    with open(class_filename, 'w') as f:
        f.write(standard_header_stuff)
        f.write(f'class {class_name}(DbModel):\n')
        f.write(f'{indent}"""Database: {db_name}, collection: {class_name}"""\n')
        for field_name, python_type in fields.items():
            f.write(f'{indent}{field_name}: {python_type}\n')
        f.write(f"{indent}_collection: ClassVar = '{class_name}'\n")


def verify_conversion_to_python_class():
    """verify that the logic to convert a collection within a database works properly."""
    database_name: str = ProgramSettings.get_setting('mongodb_database_name')
    collection_name: str = ProgramSettings.get_setting('mongodb_collection_name')
    collection_schema_dictionary = get_schema_for_collection(database_name, collection_name)
    logger.info(f'schema: {collection_schema_dictionary}')
    external_filename: str = f'{collection_name}-schema.json'
    properties_dictionary: dict = collection_schema_dictionary[0]['properties']
    write_schema_to_file(properties_dictionary, external_filename)

    class_dictionary: dict = convert_schema_dictionary_to_pyodmongo_dictionary(properties_dictionary)
    logger.info(f'{class_dictionary=}')

    class_name: str = ProgramSettings.get_setting('class_name')
    write_pyodmongo_class(database_name, class_name, class_dictionary)


if __name__ == '__main__':
    start_logging()

    msg = f'Python version {get_python_version()}'
    logger.info(msg)
    logger.debug(msg)

    msg = f'loguru version {get_package_version("loguru")}'
    logger.info(msg)
    logger.debug(msg)

    msg = f'motor version {get_package_version("motor")}'
    logger.info(msg)
    logger.debug(msg)

    msg = f'pydantic version {get_package_version("pydantic")}'
    logger.info(msg)
    logger.debug(msg)

    msg = f'PyODMongo version {get_package_version("PyODMongo")}'
    logger.info(msg)
    logger.debug(msg)

    msg = f'Pymongo version {get_package_version("Pymongo")}'
    logger.info(msg)
    logger.debug(msg)

    logger.info(f'MongoDB Atlas URI: {get_mongodb_atlas_uri()}')
    print(f'pyodmongo version: {get_package_version("pyodmongo")}')

    verify_mongodb_database()

    verify_conversion_to_python_class()
