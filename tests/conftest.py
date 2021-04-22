import asyncio
import os
import random
from contextlib import AsyncExitStack
from typing import List

import pytest
from sqlalchemy import create_engine

from explorebaduk.database import BaseModel, SessionLocal
from explorebaduk.main import app
from explorebaduk.models import BlacklistModel, FriendshipModel, UserModel
from explorebaduk.shared import UsersManager
from explorebaduk.utils.database import (
    generate_blocked_users,
    generate_friends,
    generate_users,
)

from .helpers import ApiTester, WebSocketTester

BASE_DIR = os.path.dirname(__file__)
TEST_DATABASE_PATH = os.path.join(BASE_DIR, os.path.pardir, "explorebaduk_test.sqlite3")
TEST_DATABASE_URI = f"sqlite:///{os.path.abspath(TEST_DATABASE_PATH)}"
engine = create_engine(TEST_DATABASE_URI, connect_args={"check_same_thread": False})
SessionLocal.configure(bind=engine)


@pytest.fixture
def db_session():
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def db_users(db_session) -> List[UserModel]:
    return generate_users(db_session, 20)


@pytest.fixture(autouse=True)
def db_friends(db_session, db_users) -> List[FriendshipModel]:
    return generate_friends(db_session, db_users, 5)


@pytest.fixture(autouse=True)
def db_blocked_users(db_session, db_users, db_friends) -> List[BlacklistModel]:
    return generate_blocked_users(db_session, db_users, 3, db_friends)


@pytest.fixture
async def test_cli() -> ApiTester:
    UsersManager.clear()

    async with ApiTester(app) as client:
        yield client


@pytest.fixture
async def ws(test_cli) -> WebSocketTester:
    async with test_cli.websocket_connect("/ws") as websocket:
        yield WebSocketTester(websocket)


@pytest.fixture
async def websockets(test_cli, db_users) -> List[WebSocketTester]:
    num = 5
    users = random.sample(db_users, num)

    ws_list = [
        WebSocketTester(test_cli.websocket_connect("/ws")) for _ in range(num + 3)
    ]
    async with AsyncExitStack() as stack:
        for ws in ws_list:
            await stack.enter_async_context(ws.websocket)

        await asyncio.gather(
            *[ws.authorize_as_user(user) for ws, user in zip(ws_list[:num], users)],
            *[ws.authorize_as_guest() for ws in ws_list[num:]],
        )

        await asyncio.wait([ws.receive() for ws in ws_list])

        yield ws_list
