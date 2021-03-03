import random
import uuid

import pytest
from starlette.status import HTTP_200_OK

from explorebaduk.constants import GameCategory, RuleSet, TimeSystem
from explorebaduk.messages import OpenGameCreatedMessage
from explorebaduk.schemas import OpenGame


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
    resp = await test_cli.create_game(post_body)
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
        "game_setings": {
            "handicap": 3,
            "komi": 0,
        },
    }
    resp = await test_cli.create_game(post_body)
    assert resp.status_code == HTTP_200_OK, resp.text

    game = OpenGame.parse_obj(post_body).dict()

    assert resp.json() == game

    expected = OpenGameCreatedMessage(user, game).json()
    for websocket in websockets:
        messages = await websocket.receive()
        assert messages == [expected]
