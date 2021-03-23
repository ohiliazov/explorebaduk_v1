import uuid

import pytest
from starlette.status import HTTP_200_OK

from explorebaduk.constants import GameCategory, RuleSet, TimeSystem
from explorebaduk.messages import (
    GameInviteAcceptMessage,
    GameInviteAddMessage,
    GameInviteRejectMessage,
)
from explorebaduk.schemas import GameSetup

from .helpers import random_websocket, receive_websockets


@pytest.fixture
def game_invite() -> dict:
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
        "game_settings": {
            "color": "black",
            "handicap": 3,
            "komi": 0,
        },
    }


@pytest.mark.asyncio
async def test_create_game_invite(test_cli, db_users, websockets, game_invite):
    user_ws = random_websocket(websockets)
    opponent_ws = random_websocket(websockets, exclude_users=[user_ws.user])

    test_cli.authorize(user_ws.user)

    resp = await test_cli.create_game_invite(opponent_ws.user.user_id, game_invite)
    assert resp.status_code == HTTP_200_OK, resp.text

    game = GameSetup.parse_obj(game_invite).dict()

    assert resp.json() == game

    expected = GameInviteAddMessage(user_ws.user, game).json()
    assert expected in await opponent_ws.receive()

    for messages in await receive_websockets(websockets):
        assert not messages


@pytest.mark.asyncio
async def test_accept_game_invite(test_cli, db_users, websockets, game_invite):
    user_ws = random_websocket(websockets)
    opponent_ws = random_websocket(websockets, exclude_users=[user_ws.user])

    test_cli.authorize(user_ws.user)

    resp = await test_cli.create_game_invite(opponent_ws.user.user_id, game_invite)
    assert resp.status_code == HTTP_200_OK, resp.text

    await receive_websockets(websockets)

    test_cli.authorize(opponent_ws.user)
    resp = await test_cli.accept_game_invite(user_ws.user.user_id)
    assert resp.status_code == HTTP_200_OK, resp.text
    assert resp.json() == {"message": "Game invite accepted"}

    expected = GameInviteAcceptMessage(opponent_ws.user).json()
    assert expected in await user_ws.receive()

    for messages in await receive_websockets(websockets):
        assert not messages


@pytest.mark.asyncio
async def test_reject_game_invite(test_cli, db_users, websockets, game_invite):
    user_ws = random_websocket(websockets)
    opponent_ws = random_websocket(websockets, exclude_users=[user_ws.user])

    test_cli.authorize(user_ws.user)

    resp = await test_cli.create_game_invite(opponent_ws.user.user_id, game_invite)
    assert resp.status_code == HTTP_200_OK, resp.text

    await receive_websockets(websockets)

    test_cli.authorize(opponent_ws.user)
    resp = await test_cli.reject_game_invite(user_ws.user.user_id)
    assert resp.status_code == HTTP_200_OK, resp.text
    assert resp.json() == {"message": "Game invite rejected"}

    expected = GameInviteRejectMessage(opponent_ws.user).json()
    assert expected in await user_ws.receive()

    for messages in await receive_websockets(websockets):
        assert not messages
