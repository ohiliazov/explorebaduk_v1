import asyncio
import datetime
import os
import random
import string

import pytest
from sanic.websocket import WebSocketProtocol
from sqlalchemy.orm import create_session

from explorebaduk.app import create_app
from explorebaduk.models import (
    BaseModel,
    BlockedUserModel,
    FriendModel,
    TokenModel,
    UserModel,
)


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


@pytest.yield_fixture()
def test_app():
    os.environ["DATABASE_URI"] = "sqlite:///explorebaduk_test.sqlite3"
    app = create_app()

    return app


@pytest.fixture
def test_cli(loop, test_app, test_client):
    return loop.run_until_complete(test_client(test_app, protocol=WebSocketProtocol))


@pytest.fixture
async def users_data(test_app):
    session = create_session(test_app.db_engine)
    BaseModel.metadata.drop_all(test_app.db_engine)
    BaseModel.metadata.create_all(test_app.db_engine)

    users_data = []

    for user_id in range(1, 101):
        token = f"{string.ascii_letters}{user_id:012d}"

        user_data = {
            "user_id": user_id,
            "username": f"johndoe{user_id}",
            "first_name": "John",
            "last_name": f"Doe#{user_id}",
            "email": f"johndoe{user_id}@explorebaduk.com",
            "password": "$2y$10$N5ohEZckAk/9Exus/Py/5OM7pZgr8Gk6scZpH95FjvOSRWo00tVoC",  # Abcdefg1
            "rating": random.randint(0, 3000),
            "puzzle_rating": random.randint(0, 3000),
            "avatar": f"johndoe{user_id}.png",
        }
        token_data = {
            "id": user_id,
            "user_id": user_id,
            "token": token,
            "expire": datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
        }
        user = UserModel(**user_data)
        token = TokenModel(**token_data)

        session.add_all([user, token])
        users_data.append({"user": user, "token": token, "friends": set(), "blocked_users": set()})

    for user_id, user_data in enumerate(users_data[:5], start=1):
        for friend in users_data[user_id:5]:
            friend_id = friend["user"].user_id
            friend_user_data = {
                "user_id": user_id,
                "friend_id": friend_id,
                "muted": friend_id % 2 == 0,
            }
            user_friend_data = {
                "user_id": friend_id,
                "friend_id": user_id,
                "muted": user_id > 3,
            }
            friend_user = FriendModel(**friend_user_data)
            user_friend = FriendModel(**user_friend_data)
            session.add_all([friend_user, user_friend])
            user_data["friends"].add(friend_id)
            friend["friends"].add(user_id)

        for blocked in users_data[5:11]:
            blocked_user_id = blocked["user"].user_id
            blocked_user_data = {
                "user_id": user_id,
                "blocked_user_id": blocked_user_id,
            }
            blocked_user = BlockedUserModel(**blocked_user_data)
            session.add(blocked_user)
            user_data["blocked_users"].add(blocked_user_id)

    session.flush()

    return users_data


@pytest.fixture
async def players_online(test_cli, users_data: list):
    players_online = {}

    for user_data in random.sample(users_data, 20):
        player_ws = await test_cli.ws_connect(test_cli.app.url_for("Players Feed"))
        await player_ws.send_json({"event": "authorize", "data": {"token": user_data["token"].token}})
        players_online[player_ws] = user_data

    # flush messages
    await receive_all(players_online.keys(), timeout=0.5)

    return players_online


@pytest.fixture
async def challenges_online(test_cli, users_data: list):
    challenges_online = {}

    for user_data in random.sample(users_data, 20):
        ws = await test_cli.ws_connect(
            test_cli.app.url_for("Challenges Feed"),
            headers={"Authorization": user_data["token"].token},
        )
        challenges_online[ws] = user_data

    # flush messages
    await receive_all(challenges_online.keys(), timeout=1)

    return challenges_online
