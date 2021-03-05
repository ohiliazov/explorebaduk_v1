import random
import uuid

import pytest
from starlette.status import HTTP_200_OK

from explorebaduk.constants import GameCategory, RuleSet, TimeSystem
from explorebaduk.messages import GameInviteAddMessage
from explorebaduk.schemas import GameInviteIn

from .helpers import receive_websockets


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
    user = random.choice(list(filter(lambda ws: ws.user, websockets))).user
    opponent_ws = random.choice(
        list(filter(lambda ws: ws.user and ws.user != user, websockets)),
    )

    test_cli.authorize(user)

    resp = await test_cli.create_game_invite(opponent_ws.user.user_id, game_invite)
    assert resp.status_code == HTTP_200_OK, resp.text

    game = GameInviteIn.parse_obj(game_invite).dict()

    assert resp.json() == game

    expected = GameInviteAddMessage(user, game).json()
    assert expected in await opponent_ws.receive()

    for messages in await receive_websockets(websockets):
        assert not messages
