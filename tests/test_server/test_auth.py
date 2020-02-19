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


async def receive_mesages(ws):
    responses = []
    try:
        while True:
            resp = await asyncio.wait_for(ws.recv(), timeout=1)
            responses.append(resp)

    except asyncio.TimeoutError:
        pass

    return responses


@pytest.mark.asyncio
async def test_auth_login(db_session, ws1):

    token = random_token(db_session)
    user = get_user(db_session, token.user_id)
    player = Player(ws1, user)

    await ws1.send(f"auth login {token.token}")
    messages = await receive_mesages(ws1)
    assert f"auth login OK {player}" in messages
    assert f"sync player joined {player}" in messages


@pytest.mark.asyncio
async def test_auth_login_invalid_token(ws1):
    wrong_token = "x" * 64

    await ws1.send(f"auth login {wrong_token}")
    messages = await receive_mesages(ws1)
    assert "auth login ERROR invalid token" in messages


@pytest.mark.asyncio
async def test_auth_login_already_login(db_session, ws1, ws2):

    token = random_token(db_session)
    user = get_user(db_session, token.user_id)
    player = Player(ws1, user)

    await ws1.send(f"auth login {token.token}")
    messages = await receive_mesages(ws1)
    assert f"auth login OK {player}" in messages
    assert f"sync player joined {player}" in messages

    await ws1.send(f"auth login {token.token}")
    messages = await receive_mesages(ws1)

    assert "auth login ERROR already logged in" in messages


@pytest.mark.asyncio
async def test_auth_login_online_other_device(db_session, ws1, ws2):

    token = random_token(db_session)
    user = get_user(db_session, token.user_id)
    player = Player(ws1, user)

    await ws1.send(f"auth login {token.token}")
    messages = await receive_mesages(ws1)
    assert f"auth login OK {player}" in messages
    assert f"sync player joined {player}" in messages

    messages = await receive_mesages(ws2)
    assert f"sync player joined {player}" in messages

    await ws2.send(f"auth login {token.token}")
    messages = await receive_mesages(ws2)
    assert "auth login ERROR online from other device" in messages


@pytest.mark.asyncio
async def test_auth_logout(db_session, ws1, ws2):

    token = random_token(db_session)
    user = get_user(db_session, token.user_id)
    player = Player(ws1, user)

    await ws1.send(f"auth login {token.token}")

    messages = await receive_mesages(ws1)
    assert f"auth login OK {player}" in messages
    assert f"sync player joined {player}" in messages

    messages = await receive_mesages(ws2)
    assert f"sync player joined {player}" in messages

    await ws1.send(f"auth logout")
    messages = await receive_mesages(ws1)
    assert f"auth logout OK" in messages

    messages = await receive_mesages(ws2)
    assert f"sync player left {player}" in messages
