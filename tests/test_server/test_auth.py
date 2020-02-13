import asyncio
import pytest
import random

from explorebaduk.database import UserModel, TokenModel
from explorebaduk.models import Player

CONNECTED_CLIENTS = 10


def get_user(db, user_id):
    user = db.query(UserModel).filter_by(user_id=user_id).first()
    return user


def random_token(db):
    user = random.choice(list(db.query(TokenModel).all()))
    return user


async def get_response(ws):
    responses = []
    try:
        while True:
            resp = await asyncio.wait_for(ws.recv(), timeout=1)
            responses.append(resp)

    except asyncio.TimeoutError:
        pass

    return responses


@pytest.mark.asyncio
async def test_auth_login(db_session, client_factory):
    ws1 = await client_factory()

    token = random_token(db_session)
    user = get_user(db_session, token.user_id)

    player = Player(ws1, user)
    await ws1.send(f"auth login {token.token}")

    actual = await get_response(ws1)
    expected = [
        f"auth login OK {player}",
        f"sync player joined {player}",
    ]

    assert all([message in actual for message in expected])


@pytest.mark.asyncio
async def test_auth_login_errors(client_factory):
    ws1 = await client_factory()

    wrong_token = "x" * 64

    await ws1.send(f"auth login {wrong_token}")

    actual = await get_response(ws1)
    expected = ["auth login ERROR invalid token"]

    assert all([message in actual for message in expected])
