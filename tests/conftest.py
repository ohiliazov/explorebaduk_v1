import asyncio
import random
from contextlib import AsyncExitStack
from typing import List

import pytest

from explorebaduk.database import DatabaseHandler
from explorebaduk.main import app
from explorebaduk.models import BaseModel, BlacklistModel, FriendshipModel, UserModel
from explorebaduk.managers import clear_server_state
from explorebaduk.utils.database import (
    generate_blocked_users,
    generate_friends,
    generate_users,
)

from .helpers import ApiTester, WebSocketTester


@pytest.fixture
def db():
    db = DatabaseHandler()
    BaseModel.metadata.drop_all(db.session.bind)
    BaseModel.metadata.create_all(db.session.bind)

    try:
        yield db
    finally:
        db.session.close()


@pytest.fixture(autouse=True)
def db_users(db) -> List[UserModel]:
    return generate_users(db.session, 20)


@pytest.fixture(autouse=True)
def db_friends(db, db_users) -> List[FriendshipModel]:
    return generate_friends(db.session, db_users, 5)


@pytest.fixture(autouse=True)
def db_blocked_users(db, db_users, db_friends) -> List[BlacklistModel]:
    return generate_blocked_users(db.session, db_users, 3, db_friends)


@pytest.fixture
async def test_cli() -> ApiTester:
    clear_server_state()

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
