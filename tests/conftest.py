import pytest
from sqlalchemy import create_engine

from config import get_config
from explorebaduk.database import BaseModel
from scripts.database import (
    make_user,
    make_token,
    populate_database_with_data,
)
from explorebaduk.database import DatabaseHandler


config = get_config(env="test")
db = DatabaseHandler(config['database_uri'])


@pytest.fixture(scope="session", autouse=True)
def db_handler():
    BaseModel.metadata.drop_all(db.engine)
    BaseModel.metadata.create_all(db.engine)
    populate_database_with_data(db, 20)

    return db


@pytest.fixture(scope="session")
def user1(db_handler):
    user = make_user(1)

    db_handler.session.save(user)

    return user


@pytest.fixture(scope="session")
def token1(db_handler, user1):
    token = make_token(user1.user_id, user1.user_id, 60)

    db_handler.session.save(token)

    return token


@pytest.fixture(scope="session")
def token_expired(db_handler, user1):
    token = make_token(666, user1.user_id, 0)

    db_handler.session.save(token)

    return token
