import random
import uuid

import pytest
from starlette.status import HTTP_200_OK

from explorebaduk.constants import GameCategory, RuleSet, TimeSystem
from explorebaduk.messages import GameInviteAddMessage, OpenGameCreatedMessage
from explorebaduk.schemas import DirectGame, OpenGame


@pytest.mark.asyncio
async def test_create_open_game(test_cli, db_users, websockets):
    user = random.choice(list(filter(lambda ws: ws.user, websockets))).user
    test_cli.authorize(user)

    post_body = {
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
    resp = await test_cli.create_open_game(post_body)
    assert resp.status_code == HTTP_200_OK, resp.text

    game = OpenGame.parse_obj(post_body).dict()

    assert resp.json() == game

    expected = OpenGameCreatedMessage(user, game).json()
    for websocket in websockets:
        messages = await websocket.receive()
        assert messages == [expected]


@pytest.mark.asyncio
async def test_create_direct_invite(test_cli, db_users, websockets):
    user = random.choice(list(filter(lambda ws: ws.user, websockets))).user
    opponent_ws = random.choice(
        list(filter(lambda ws: ws.user and ws.user != user, websockets)),
    )

    test_cli.authorize(user)

    post_body = {
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

    resp = await test_cli.create_direct_game(opponent_ws.user.user_id, post_body)
    assert resp.status_code == HTTP_200_OK, resp.text

    game = DirectGame.parse_obj(post_body).dict()

    assert resp.json() == game

    expected = GameInviteAddMessage(user, game).json()
    assert expected in await opponent_ws.receive()

    for websocket in websockets:
        assert not await websocket.receive()
