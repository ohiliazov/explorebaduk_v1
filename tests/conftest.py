import pytest
from sqlalchemy import create_engine

from config import TEST_DATABASE_URI
from explorebaduk.database import create_session, BaseModel
from explorebaduk.utils.database import make_user, make_token


@pytest.fixture(scope='session')
def engine():
    return create_engine(TEST_DATABASE_URI)


@pytest.yield_fixture(scope='session')
def db(engine):
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)

    db = create_session(TEST_DATABASE_URI, expire_on_commit=True)

    return db


@pytest.fixture(scope='session')
def user1(db):
    user = make_user(1)

    db.add(user)

    return user


@pytest.fixture(scope='session')
def token1(db, user1):
    token = make_token(user1.user_id, user1.user_id, 60)

    db.add(token)

    return token


@pytest.fixture(scope='session')
def token_expired(db, user1):
    token = make_token(666, user1.user_id, 0)

    db.add(token)

    return token
