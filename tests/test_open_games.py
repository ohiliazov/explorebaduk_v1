import uuid

import pytest
from starlette.status import HTTP_200_OK

from explorebaduk.constants import GameCategory, RuleSet, TimeSystem
from explorebaduk.messages import (
    AcceptOpenGameRequestMessage,
    CreateOpenGameRequestMessage,
    OpenGameCreatedMessage,
    OpenGameRemoveMessage,
    RejectOpenGameRequestMessage,
)
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
    user_ws = random_websocket(websockets)
    test_cli.authorize(user_ws.user)

    resp = await test_cli.create_open_game(open_game)
    assert resp.status_code == HTTP_200_OK, resp.text

    game = OpenGame.parse_obj(open_game).dict()

    assert resp.json() == game

    expected = OpenGameCreatedMessage(user_ws.user, game).json()

    for messages in await receive_websockets(websockets):
        assert messages == [expected]


@pytest.mark.asyncio
async def test_cancel_open_game(test_cli, db_users, websockets, open_game):
    user_ws = random_websocket(websockets)
    test_cli.authorize(user_ws.user)

    resp = await test_cli.create_open_game(open_game)
    assert resp.status_code == HTTP_200_OK, resp.text

    await receive_websockets(websockets)

    resp = await test_cli.cancel_open_game()
    assert resp.status_code == HTTP_200_OK, resp.text
    assert resp.json() == {"message": "Open game cancelled"}

    expected = OpenGameRemoveMessage(user_ws.user).json()
    for messages in await receive_websockets(websockets):
        assert messages == [expected]


@pytest.mark.asyncio
async def test_request_open_game(test_cli, db_users, websockets, open_game):
    user_ws = random_websocket(websockets)
    test_cli.authorize(user_ws.user)

    resp = await test_cli.create_open_game(open_game)
    assert resp.status_code == HTTP_200_OK, resp.text

    await receive_websockets(websockets)

    opponent_ws = random_websocket(websockets, exclude_users=[user_ws.user])
    test_cli.authorize(opponent_ws.user)

    post_body = {"color": "black", "handicap": 3, "komi": 0.5}
    resp = await test_cli.request_open_game(user_ws.user.user_id, post_body)
    assert resp.status_code == HTTP_200_OK, resp.text
    assert resp.json() == {"message": "Game requested"}

    expected = CreateOpenGameRequestMessage(opponent_ws.user, post_body).json()
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
    resp = await test_cli.accept_open_game(opponent_ws.user.user_id)
    assert resp.status_code == HTTP_200_OK, resp.text
    assert resp.json() == {"message": "Game accepted"}

    expected = [
        AcceptOpenGameRequestMessage(user_ws.user).json(),
        OpenGameRemoveMessage(user_ws.user).json(),
    ]
    assert await opponent_ws.receive() == expected

    expected = [OpenGameRemoveMessage(user_ws.user).json()]
    for messages in await receive_websockets(websockets, [opponent_ws]):
        assert messages == expected


@pytest.mark.asyncio
async def test_reject_open_game(test_cli, db_users, websockets, open_game):
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
    resp = await test_cli.reject_open_game(opponent_ws.user.user_id)
    assert resp.status_code == HTTP_200_OK, resp.text
    assert resp.json() == {"message": "Game rejected"}

    expected = RejectOpenGameRequestMessage(user_ws.user).json()
    assert await opponent_ws.receive() == [expected]

    for messages in await receive_websockets(websockets):
        assert not messages
