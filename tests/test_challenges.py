import pytest
from starlette.status import HTTP_200_OK

from explorebaduk.crud import DatabaseHandler
from explorebaduk.messages import ChallengeCreatedMessage
from tests.helpers import random_websocket, receive_websockets


@pytest.fixture
def challenge_json() -> dict:
    return {
        "game": {
            "name": "string",
            "private": False,
            "ranked": True,
            "board_size": 19,
            "speed": "blitz",
            "rules": "japanese",
            "time_control": {
                "time_system": "byo-yomi",
                "main_time": 1800,
                "overtime": 30,
                "periods": 5,
            },
            "handicap": None,
            "komi": None,
        },
        "creator_color": "nigiri",
        "min_rating": None,
        "max_rating": None,
    }


@pytest.mark.asyncio
async def test_create_challenge(test_cli, db_users, websockets, challenge_json):
    user_ws = random_websocket(websockets)
    test_cli.authorize(user_ws.user)

    resp = await test_cli.create_challenge(challenge_json)
    assert resp.status_code == HTTP_200_OK, resp.text

    with DatabaseHandler() as db:
        challenge = db.get_challenge_by_id(resp.json()["challenge_id"])
        expected = ChallengeCreatedMessage(challenge).json()

    for messages in await receive_websockets(websockets):
        assert expected in messages
