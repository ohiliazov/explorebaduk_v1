import asyncio
import os
import random
import uuid

import pytest
from sanic.websocket import WebSocketProtocol
from sqlalchemy.orm import create_session

from explorebaduk.app import create_app
from explorebaduk.models import BaseModel
from explorebaduk.utils.database import (
    generate_blocked_users,
    generate_friends,
    generate_tokens,
    generate_users,
)

TEST_DATABASE_URI = "sqlite:///explorebaduk_test.sqlite3"


async def receive_messages(ws, sort_by: callable = None, timeout: float = 0.5):
    messages = []
    try:
        while True:
            messages.append(await ws.receive_json(timeout=timeout))
    except asyncio.TimeoutError:
        pass

    if sort_by:
        messages = sorted(messages, key=sort_by)

    return messages


async def receive_all(ws_list, sort_by: callable = None, timeout: float = 0.5):
    return await asyncio.gather(*[receive_messages(ws, sort_by, timeout) for ws in ws_list])


@pytest.fixture
def test_app():
    os.putenv("DATABASE_URI", TEST_DATABASE_URI)
    app = create_app(str(uuid.uuid4()))

    return app


@pytest.fixture
def test_cli(loop, test_app, sanic_client):
    return loop.run_until_complete(sanic_client(test_app, protocol=WebSocketProtocol))


@pytest.fixture
async def users_data(test_app):
    session = create_session(test_app.db_engine)
    BaseModel.metadata.drop_all(test_app.db_engine)
    BaseModel.metadata.create_all(test_app.db_engine)

    users = generate_users(session, 100)
    tokens = generate_tokens(session, users, minutes=60)
    expired_tokens = generate_tokens(session, users, minutes=-60)
    friends = generate_friends(session, users, 5)
    blocked_users = generate_blocked_users(session, users, 5, friends)

    users_data = []
    for user in users:
        users_data.append(
            {
                "user": user,
                "token": [token for token in tokens if token.user_id == user.user_id][0],
                "expired_token": [
                    expired_token for expired_token in expired_tokens if expired_token.user_id == user.user_id
                ][0],
                "friends": {friend.friend_id for friend in friends},
                "blocked_users": {blocked_user.blocked_user_id for blocked_user in blocked_users},
            },
        )

    return users_data


async def authorized_connections(test_cli, users_data: list, feed_name: str, ws_count: int):
    ws_list = await asyncio.gather(*[test_cli.ws_connect(test_cli.app.url_for(feed_name)) for _ in range(ws_count)])

    await asyncio.gather(
        *[
            ws.send_json({"event": "authorize", "data": {"token": user_data["token"].token}})
            for ws, user_data in zip(ws_list, users_data)
        ]
    )
    await receive_all(ws_list, timeout=0.5)

    return {ws: user_data for ws, user_data in zip(ws_list, users_data)}


@pytest.fixture
async def players_online(test_cli, users_data: list):
    return await authorized_connections(test_cli, random.sample(users_data, 20), "Players Feed", 30)


@pytest.fixture
async def challenges_online(test_cli, users_data: list):
    return await authorized_connections(test_cli, random.sample(users_data, 20), "Challenges Feed", 30)


@pytest.fixture
async def challenge_owners_online(test_cli, users_data: list):
    users_data = random.sample(users_data, 20)

    ws_list = await asyncio.gather(
        *[
            test_cli.ws_connect(test_cli.app.url_for("Challenge Owner Feed", challenge_id=user_data["user"].user_id))
            for user_data in users_data
        ]
    )

    await asyncio.gather(
        *[
            ws.send_json({"event": "authorize", "data": {"token": user_data["token"].token}})
            for ws, user_data in zip(ws_list, users_data)
        ]
    )
    await receive_all(ws_list, timeout=0.5)

    return {ws: user_data for ws, user_data in zip(ws_list, users_data)}
