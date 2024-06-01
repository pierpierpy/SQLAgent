import time
from typing import Dict
import jwt
import bcrypt
from src.database.interaction import get_users_db
import models.auth as mauth
import os
from sqlalchemy import Engine

JWT_SECRET = os.environ.get("secret")
JWT_ALGORITHM = os.environ.get("algorithm")
EXPIRATION = 3000


def token_response(token: str):
    return {"access_token": token, "expiration": EXPIRATION}


def signJWT(user_id: str) -> Dict[str, str]:
    # TODO[] mettere l'expiration del bearer token nelle env variables
    payload = {"user_id": user_id, "expires": time.time() + EXPIRATION}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}


def hash_password(password: str) -> str:
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed_password.decode("utf-8")


def check_user(engine: Engine, data: mauth.UserLoginSchema):

    for user in get_users_db(engine):
        if user.email == data.email and bcrypt.checkpw(
            data.password.encode("utf-8"), user.password.encode("utf-8")
        ):
            return True
