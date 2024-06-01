from sqlalchemy import inspect, Engine
from sqlalchemy.exc import OperationalError
from decouple import config
from src.database.models import Base, User, Report, ConversationOwnership

tables_to_create = [ConversationOwnership]


def check_connection(engine: Engine) -> bool:
    """check connection to db, returns True if connection is alright, else False

    Args:
        engine (Engine): _description_

    Returns:
        bool: _description_
    """
    try:
        connection = engine.connect()
        connection.close()
        return True
    except OperationalError as e:
        return False


def table_exists(engine: Engine, schema: str) -> bool:
    """check if table exists

    Args:
        engine (Engine): _description_
        schema (str): _description_

    Returns:
        bool: _description_
    """
    insp = inspect(engine)
    return insp.has_table(config("db_name"), schema=schema)


def create_tables(engine: Engine) -> bool:
    """create table (used only for users)

    Args:
        engine (Engine): _description_

    Returns:
        bool: _description_
    """
    if not check_connection(engine):
        return False
    insp = inspect(engine)
    if not all(table_exists(insp, schema.__tablename__) for schema in tables_to_create):
        try:
            Base.metadata.create_all(engine)
            return True
        except OperationalError as e:
            print(f"an error occurred: {e}")
            return False
    else:
        return False


def drop_table(engine: Engine) -> bool:
    """drop table (only for users)

    Args:
        engine (Engine): _description_

    Returns:
        bool: _description_
    """
    if not check_connection(engine):
        return False
    insp = inspect(engine)
    if not all(table_exists(insp, schema.__tablename__) for schema in tables_to_create):
        try:
            Base.metadata.drop_all(engine)
            return True
        except OperationalError as e:
            print(f"an error occurred: {e}")
            return False
    else:
        return False
