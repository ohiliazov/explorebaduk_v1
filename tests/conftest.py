import asyncio
import websockets
import pytest
from sqlalchemy import create_engine

from config import TEST_DATABASE_URI, TEST_SERVER_HOST, TEST_SERVER_PORT
from explorebaduk.database import create_session, BaseModel
from explorebaduk.utils.database import make_user, make_token
from app import start_server


@pytest.fixture
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture
async def start_test_server(event_loop):
    await websockets.serve(start_server, TEST_SERVER_HOST, TEST_SERVER_PORT, loop=event_loop)


@pytest.fixture
def client_factory(event_loop):
    async def wrapped():
        return await websockets.connect(f'ws://{TEST_SERVER_HOST}:{TEST_SERVER_PORT}', loop=event_loop)
    return wrapped


@pytest.fixture(scope="session")
def engine():
    return create_engine(TEST_DATABASE_URI)


@pytest.yield_fixture(scope="session")
def db(engine):
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)

    db = create_session(TEST_DATABASE_URI, expire_on_commit=True)

    return db


@pytest.fixture(scope="session")
def user1(db):
    user = make_user(1)

    db.add(user)

    return user


@pytest.fixture(scope="session")
def token1(db, user1):
    token = make_token(user1.user_id, user1.user_id, 60)

    db.add(token)

    return token


@pytest.fixture(scope="session")
def token_expired(db, user1):
    token = make_token(666, user1.user_id, 0)

    db.add(token)

    return token
