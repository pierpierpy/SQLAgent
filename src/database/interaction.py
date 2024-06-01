from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker
from src.database.models import (
    User,
    MessageStore,
    SQLMessageStore,
    ConversationOwnership,
)
import src.database.init as db
from typing import Dict, List
import json


# TODO[] check if the user already exists
def create_user_db(engine: Engine, fullname: str, email: str, password: str) -> None:
    """create user in db with hashed password

    Args:
        engine (Engine): _description_
        fullname (str): _description_
        email (str): _description_
        password (str): _description_

    Returns:
        _type_: _description_
    """

    session = sessionmaker(bind=engine)
    Session = session()
    try:
        new_user = User(fullname=fullname, email=email, password=password)
        Session.add(new_user)
        Session.commit()
    except Exception as e:
        Session.rollback()
    finally:
        Session.close()


def get_users_db(engine: Engine) -> List[User]:
    """get the users registered as objects

    Args:
        engine (Engine): _description_

    Returns:
        _type_: _description_
    """

    session = sessionmaker(bind=engine)
    Session = session()
    users = Session.query(User).all()
    Session.close()
    return users


def get_users_as_dicts(engine: Engine) -> List[Dict[str, str]]:
    """get users as a dictionary

    Args:
        engine (Engine): _description_

    Returns:
        _type_: _description_
    """

    session = sessionmaker(bind=engine)
    Session = session()
    users = Session.query(User).all()
    user_dicts = []
    for user in users:
        user_dict = {
            "id": user.id,
            "fullname": user.fullname,
            "email": user.email,
            "password": user.password,
        }
        user_dicts.append(user_dict)
    Session.close()
    return user_dicts


def get_conversations_as_dicts(engine: Engine) -> Dict[str, None]:
    """restore conversations as a dictionary from db.

    Args:
        engine (Engine): _description_

    Returns:
        _type_: _description_
    """

    session = sessionmaker(bind=engine)
    Session = session()
    conversations = Session.query(MessageStore).all()
    conversation_ids = dict.fromkeys(
        [conversation.session_id for conversation in conversations]
    )

    Session.close()
    return conversation_ids


def get_conversation_check(engine: Engine, conversation_id: str) -> bool:
    """check conversation id existance

    Args:
        engine (Engine): _description_

    Returns:
        _type_: _description_
    """
    if not db.check_connection(engine=engine):
        return False
    session = sessionmaker(bind=engine)
    Session = session()
    conversations = Session.query(MessageStore).all()
    if conversations is None:
        return True
    conversation_ids = [conversation.session_id for conversation in conversations]
    Session.close()
    check = conversation_id in conversation_ids
    return check


def get_memory_by_conversation_id(
    engine: Engine, conversation_id: str
):  # TODO[] aggiusta l'output data type
    """get the memory from a particular conversation id

    Args:
        engine (Engine): _description_

    Returns:
        _type_: _description_
    """
    if not db.check_connection(engine=engine):
        return False
    session = sessionmaker(bind=engine)
    Session = session()
    messages = Session.query(MessageStore).filter(
        MessageStore.session_id
        == conversation_id  # TODO[] qui il conversation id l'ho chiamato session id e non so il motivo. forse andrebbe rinominato conversation id
    )
    conversation = []
    for message in messages:
        user_dict = {
            "message": message.message,
        }
        conversation.append(user_dict)

    Session.close()
    return conversation


def clear_memory_by_conversation_id(engine: Engine, conversation_id: str):
    if not db.check_connection(engine=engine):
        return False
    session = sessionmaker(bind=engine)
    Session = session()
    # TODO[] some error handling here with transactions... and rollbacks (same thing for all the other db interaction functions)
    Session.query(MessageStore).filter(
        MessageStore.session_id == conversation_id
    ).delete()
    Session.query(SQLMessageStore).filter(
        SQLMessageStore.session_id == conversation_id
    ).delete()
    Session.query(ConversationOwnership).filter(
        ConversationOwnership.conversation_id == conversation_id
    ).delete()
    Session.commit()
    Session.close()
    return conversation_id


def create_user_conversation_ownership(
    engine: Engine, conversation_id: str, user_id: str
):
    if not db.check_connection(engine=engine):
        return False
    # TODO create table if not exists
    if not db.table_exists(engine=engine, schema="conversation_owners"):
        db.create_tables(engine=engine)
    session = sessionmaker(bind=engine)
    Session = session()
    try:
        new_ownership = ConversationOwnership(
            conversation_id=conversation_id, user_id=user_id, number_of_messages=0
        )
        Session.add(new_ownership)
        Session.commit()
    except Exception as e:
        Session.rollback()
    finally:
        Session.close()


def update_number_of_messages_owner_conversation(engine: Engine, conversation_id: str):
    if not db.check_connection(engine=engine):
        return False
    session = sessionmaker(bind=engine)
    Session = session()
    try:
        Session.query(ConversationOwnership).filter(
            ConversationOwnership.conversation_id == conversation_id
        ).update({"number_of_messages": ConversationOwnership.number_of_messages + 2})
        Session.commit()
    except Exception as e:
        Session.rollback()
    finally:
        Session.close()


def get_conversation_by_user_id_conversation_id(
    engine: Engine, conversation_id: str, user_id: str
):
    if not db.check_connection(engine=engine):
        return False
    session = sessionmaker(bind=engine)
    Session = session()

    owned_by_user_id = Session.query(ConversationOwnership).filter(
        ConversationOwnership.user_id == user_id
    )
    conversations_owned_by_user_id = [
        conversations_owned_by_user_id.conversation_id
        for conversations_owned_by_user_id in owned_by_user_id
    ]
    # anche se vuota, la conversazione viene ritornata
    if conversation_id in conversations_owned_by_user_id:
        return {
            "owned": True,
            "convs": [
                json.loads(message.message)
                for message in Session.query(MessageStore)
                .filter(MessageStore.session_id == conversation_id)
                .all()
            ],
        }
    else:
        # conversation not owned by the user
        return False


def get_conversation_id_by_user_id(engine: Engine, user_id: str):
    if not db.check_connection(engine=engine):
        return False
    session = sessionmaker(bind=engine)
    Session = session()

    owned_by_user_id = Session.query(ConversationOwnership).filter(
        ConversationOwnership.user_id == user_id
    )
    conversations_owned_by_user_id = [
        conversations_owned_by_user_id.conversation_id
        for conversations_owned_by_user_id in owned_by_user_id
    ]
    return conversations_owned_by_user_id
