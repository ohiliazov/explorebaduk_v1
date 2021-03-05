import uuid

import pytest
from starlette.status import HTTP_200_OK

from explorebaduk.constants import GameCategory, RuleSet, TimeSystem
from explorebaduk.messages import OpenGameCreatedMessage, OpenGameRequestMessage
from explorebaduk.schemas import OpenGame

from .helpers import random_websocket, receive_websockets


@pytest.fixture
def open_game() -> dict:
    return {
        "name": f"My Game {uuid.uuid4()}",
        "category": GameCategory.REAL_TIME.value,
        "rules": RuleSet.JAPANESE.value,
        "time_settings": {
            "time_system": TimeSystem.BYOYOMI.value,
            "main_time": 3600,
            "overtime": 60,
            "periods": 5,
        },
        "restrictions": {
            "min_rating": 1900,
            "max_rating": 2400,
            "min_handicap": 0,
            "max_handicap": 9,
        },
    }


@pytest.mark.asyncio
async def test_create_open_game(test_cli, db_users, websockets, open_game):
    user_ws = random_websocket(websockets, exclude_guests=True)
    test_cli.authorize(user_ws.user)

    resp = await test_cli.create_open_game(open_game)
    assert resp.status_code == HTTP_200_OK, resp.text

    game = OpenGame.parse_obj(open_game).dict()

    assert resp.json() == game

    expected = OpenGameCreatedMessage(user_ws.user, game).json()

    for messages in await receive_websockets(websockets):
        assert messages == [expected]


@pytest.mark.asyncio
async def test_request_open_game(test_cli, db_users, websockets, open_game):
    user_ws = random_websocket(websockets, exclude_guests=True)
    test_cli.authorize(user_ws.user)

    resp = await test_cli.create_open_game(open_game)
    assert resp.status_code == HTTP_200_OK, resp.text

    # flush
    await receive_websockets(websockets)

    opponent_ws = random_websocket(websockets, exclude_users=[user_ws.user])
    test_cli.authorize(opponent_ws.user)

    post_body = {"color": "black", "handicap": 3, "komi": 0.5}
    resp = await test_cli.request_open_game(user_ws.user.user_id, post_body)
    assert resp.status_code == HTTP_200_OK, resp.text
    assert resp.json() == {"message": "Game requested"}

    expected = OpenGameRequestMessage(opponent_ws.user, post_body).json()
    assert await user_ws.receive() == [expected]

    for messages in await receive_websockets(websockets):
        assert not messages


@pytest.mark.asyncio
async def test_accept_open_game(test_cli, db_users, websockets, open_game):
    user_ws = random_websocket(websockets, exclude_guests=True)
    test_cli.authorize(user_ws.user)

    resp = await test_cli.create_open_game(open_game)
    assert resp.status_code == HTTP_200_OK, resp.text

    opponent_ws = random_websocket(websockets, exclude_users=[user_ws.user])
    test_cli.authorize(opponent_ws.user)

    post_body = {"color": "black", "handicap": 3, "komi": 0.5}
    resp = await test_cli.request_open_game(user_ws.user.user_id, post_body)
    assert resp.status_code == HTTP_200_OK, resp.text

    # flush
    await receive_websockets(websockets)

    test_cli.authorize(user_ws.user)
    assert False
