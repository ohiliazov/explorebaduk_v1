import asyncio
import pytest
import random

from explorebaduk.database import UserModel, TokenModel
from explorebaduk.models import User

CONNECTED_CLIENTS = 10


def get_user(db, user_id):
    user = db.query(UserModel).filter_by(user_id=user_id).first()
    return user


def random_token(db):
    user = random.choice(list(db.query(TokenModel).all()))
    return user


async def receive_messages(ws):
    responses = []
    try:
        while True:
            resp = await asyncio.wait_for(ws.recv(), timeout=1)
            responses.append(resp)

    except asyncio.TimeoutError:
        pass

    return responses


@pytest.mark.asyncio
async def test_auth_login(db_handler, ws):

    token = random_token(db_handler)
    user = get_user(db_handler, token.user_id)
    player = User(ws, user)

    await ws.send(f"auth login {token.token}")
    messages = await receive_messages(ws)
    assert f"OK [auth login] {player}" in messages
    assert f"players add {player}" in messages


@pytest.mark.asyncio
async def test_auth_login_invalid_token(ws):
    wrong_token = "x" * 64

    await ws.send(f"auth login {wrong_token}")
    messages = await receive_messages(ws)
    assert "ERROR [auth login] invalid token" in messages


@pytest.mark.asyncio
async def test_auth_login_already_login(db_handler, ws):

    token = random_token(db_handler)
    user = get_user(db_handler, token.user_id)
    player = User(ws, user)

    await ws.send(f"auth login {token.token}")
    messages = await receive_messages(ws)
    assert f"OK [auth login] {player}" in messages
    assert f"players add {player}" in messages

    await ws.send(f"auth login {token.token}")
    messages = await receive_messages(ws)

    assert "ERROR [auth login] already logged in" in messages


@pytest.mark.asyncio
async def test_auth_login_online_other_device(db_handler, ws_factory):
    ws1, ws2 = await ws_factory(2)

    token = random_token(db_handler)
    user = get_user(db_handler, token.user_id)
    player = User(ws1, user)

    await ws1.send(f"auth login {token.token}")
    messages = await receive_messages(ws1)
    assert f"OK [auth login] {player}" in messages
    assert f"players add {player}" in messages

    messages = await receive_messages(ws2)
    assert f"players add {player}" in messages

    await ws2.send(f"auth login {token.token}")
    messages = await receive_messages(ws2)
    assert "ERROR [auth login] online from other device" in messages


@pytest.mark.asyncio
async def test_auth_logout(db_handler, ws_factory):
    ws1, ws2 = await ws_factory(2)

    token = random_token(db_handler)
    user = get_user(db_handler, token.user_id)
    player = User(ws1, user)

    await ws1.send(f"auth login {token.token}")

    messages = await receive_messages(ws1)
    assert f"OK [auth login] {player}" in messages
    assert f"players add {player}" in messages

    messages = await receive_messages(ws2)
    assert f"players add {player}" in messages

    await ws1.send(f"auth logout")
    messages = await receive_messages(ws1)
    assert f"OK [auth logout] {player}" in messages

    messages = await receive_messages(ws2)
    assert f"players del {player}" in messages
