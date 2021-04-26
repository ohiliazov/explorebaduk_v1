import pytest
from starlette.status import HTTP_200_OK, HTTP_403_FORBIDDEN

from explorebaduk.crud import DatabaseHandler
from explorebaduk.messages import (
    ChallengeAcceptedMessage,
    ChallengeOpenMessage,
    ChallengeRemovedMessage,
    DirectChallengeMessage,
)
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
async def test_create_challenge(test_cli, websockets, challenge_json):
    creator_ws = random_websocket(websockets)
    test_cli.authorize(creator_ws.user)

    resp = await test_cli.create_challenge(challenge_json)
    assert resp.status_code == HTTP_200_OK, resp.text

    with DatabaseHandler() as db:
        challenge = db.get_challenge_by_id(resp.json()["challenge_id"])
        expected = ChallengeOpenMessage(challenge).json()

    for messages in await receive_websockets(websockets):
        assert expected in messages


@pytest.mark.asyncio
async def test_accept_challenge(test_cli, websockets, challenge_json):
    creator_ws = random_websocket(websockets)
    test_cli.authorize(creator_ws.user)

    resp = await test_cli.create_challenge(challenge_json)
    assert resp.status_code == HTTP_200_OK, resp.text

    await receive_websockets(websockets)

    challenge_id = resp.json()["challenge_id"]
    with DatabaseHandler() as db:
        challenge = db.get_challenge_by_id(challenge_id)
        expected = ChallengeAcceptedMessage(challenge).json()

    opponent_ws = random_websocket(websockets, exclude_users=[creator_ws.user])
    test_cli.authorize(opponent_ws.user)

    resp = await test_cli.accept_challenge(challenge_id)
    assert resp.status_code == HTTP_200_OK, resp.text

    for messages in await receive_websockets(websockets):
        assert expected in messages


@pytest.mark.asyncio
async def test_cancel_challenge(test_cli, websockets, challenge_json):
    creator_ws = random_websocket(websockets)
    test_cli.authorize(creator_ws.user)

    resp = await test_cli.create_challenge(challenge_json)
    assert resp.status_code == HTTP_200_OK, resp.text

    await receive_websockets(websockets)

    challenge_id = resp.json()["challenge_id"]
    with DatabaseHandler() as db:
        challenge = db.get_challenge_by_id(challenge_id)
        expected = ChallengeRemovedMessage(challenge).json()

    resp = await test_cli.cancel_challenge(challenge_id)
    assert resp.status_code == HTTP_200_OK, resp.text

    for messages in await receive_websockets(websockets):
        assert expected in messages


@pytest.mark.asyncio
async def test_accept_challenge_self(test_cli, websockets, challenge_json):
    creator_ws = random_websocket(websockets)
    test_cli.authorize(creator_ws.user)

    resp = await test_cli.create_challenge(challenge_json)
    assert resp.status_code == HTTP_200_OK, resp.text

    await receive_websockets(websockets)

    challenge_id = resp.json()["challenge_id"]

    resp = await test_cli.accept_challenge(challenge_id)
    assert resp.status_code == HTTP_403_FORBIDDEN, resp.text


@pytest.mark.asyncio
async def test_cancel_challenge_not_self(test_cli, websockets, challenge_json):
    creator_ws = random_websocket(websockets)
    test_cli.authorize(creator_ws.user)

    resp = await test_cli.create_challenge(challenge_json)
    assert resp.status_code == HTTP_200_OK, resp.text

    await receive_websockets(websockets)

    challenge_id = resp.json()["challenge_id"]

    user_ws = random_websocket(websockets, exclude_users=[creator_ws.user])
    test_cli.authorize(user_ws.user)

    resp = await test_cli.cancel_challenge(challenge_id)
    assert resp.status_code == HTTP_403_FORBIDDEN, resp.text


@pytest.mark.asyncio
async def test_create_direct_challenge(test_cli, websockets, challenge_json):
    creator_ws = random_websocket(websockets)
    test_cli.authorize(creator_ws.user)

    opponent_ws = random_websocket(websockets)
    challenge_json["opponent_id"] = opponent_ws.user.user_id

    resp = await test_cli.create_challenge(challenge_json)
    assert resp.status_code == HTTP_200_OK, resp.text

    with DatabaseHandler() as db:
        challenge = db.get_challenge_by_id(resp.json()["challenge_id"])
        expected = DirectChallengeMessage(challenge).json()

    assert expected in await opponent_ws.receive()

    for messages in await receive_websockets(websockets):
        assert not messages


@pytest.mark.asyncio
async def test_accept_direct_challenge(test_cli, websockets, challenge_json):
    creator_ws = random_websocket(websockets)
    test_cli.authorize(creator_ws.user)

    opponent_ws = random_websocket(websockets, exclude_users=[creator_ws.user])
    challenge_json["opponent_id"] = opponent_ws.user.user_id

    resp = await test_cli.create_challenge(challenge_json)
    assert resp.status_code == HTTP_200_OK, resp.text

    await receive_websockets(websockets)

    challenge_id = resp.json()["challenge_id"]
    with DatabaseHandler() as db:
        challenge = db.get_challenge_by_id(challenge_id)
        expected = ChallengeAcceptedMessage(challenge).json()

    test_cli.authorize(opponent_ws.user)

    resp = await test_cli.accept_challenge(challenge_id)
    assert resp.status_code == HTTP_200_OK, resp.text

    assert expected in await creator_ws.receive()

    for messages in await receive_websockets(websockets):
        assert not messages
