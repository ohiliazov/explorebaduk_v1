import asyncio
import os
import pytest
import random
import string
import datetime

from sanic.websocket import WebSocketProtocol
from sqlalchemy.orm import create_session

from explorebaduk.app import create_app
from explorebaduk.database import BaseModel, PlayerModel, TokenModel


async def receive_messages(ws, sort_by: callable = None):
    messages = []
    try:
        while True:
            messages.append(await ws.receive_json(timeout=0.5))
    except asyncio.TimeoutError:
        pass

    if sort_by:
        messages = sorted(messages, key=sort_by)

    return messages


async def receive_all(ws_list, sort_by: callable = None):
    return await asyncio.gather(*[receive_messages(ws, sort_by) for ws in ws_list])


@pytest.yield_fixture()
def test_app():
    os.environ["CONFIG_PATH"] = "config/test.cfg"
    app = create_app()

    return app


@pytest.fixture
def test_cli(loop, test_app, test_client):
    return loop.run_until_complete(test_client(test_app, protocol=WebSocketProtocol))


@pytest.fixture
async def players_data(test_app):
    session = create_session(test_app.db_engine)
    BaseModel.metadata.drop_all(test_app.db_engine)
    BaseModel.metadata.create_all(test_app.db_engine)

    players_data = []

    for user_id in range(1, 101):
        token = f"{string.ascii_letters}{user_id:012d}"

        player_data = {
            "user_id": user_id,
            "first_name": "John",
            "last_name": f"Doe#{user_id}",
            "email": f"johndoe{user_id}@explorebaduk.com",
            "rating": random.randint(0, 3000),
            "puzzle_rating": random.randint(0, 3000),
        }
        token_data = {
            "token_id": user_id,
            "user_id": user_id,
            "token": token,
            "expired_at": datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
        }
        player = PlayerModel(**player_data)
        token = TokenModel(**token_data)
        session.add(player)
        session.add(token)
        players_data.append({
            "player": player,
            "token": token,
        })
    session.flush()

    return players_data


@pytest.fixture
async def players_online(test_cli, players_data: list):
    players_online = {}

    for player_data in random.sample(players_data, 20):
        player_ws = await test_cli.ws_connect(
            test_cli.app.url_for("Players Feed"),
            headers={"Authorization": player_data["token"].token},
        )
        players_online[player_ws] = player_data["player"]

    # flush messages
    await receive_all(players_online.keys())

    return players_online


@pytest.fixture
async def challenges_data(test_cli):
    pass
