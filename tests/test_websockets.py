import asyncio
import random

import pytest

from explorebaduk.messages import (
    PlayerOfflineMessage,
    PlayerOnlineMessage,
    WhoAmIMessage,
)

from .helpers import get_offline_users, random_websocket, receive_websockets


@pytest.mark.asyncio
async def test_authorize_as_guest(test_cli, websockets, ws):
    await ws.authorize_as_guest()

    messages = await ws.receive()

    assert WhoAmIMessage(None).json() in messages

    for websocket in websockets:
        if websocket.user:
            assert PlayerOnlineMessage(websocket.user).json() in messages


@pytest.mark.asyncio
async def test_authorize_as_user(test_cli, db_users, websockets, ws):
    user = random.choice(get_offline_users(db_users, websockets))
    await ws.authorize_as_user(user)

    messages = await ws.receive()

    assert WhoAmIMessage(user).json() in messages

    for websocket in websockets:
        if websocket.user:
            assert PlayerOnlineMessage(websocket.user).json() in messages

    expected = PlayerOnlineMessage(user).json()
    for messages in await receive_websockets(websockets, [ws]):
        assert expected in messages


@pytest.mark.asyncio
async def test_interrupted_connection(test_cli, db_users, websockets, ws):
    user_ws = random_websocket(websockets)

    await user_ws.websocket.close(1000)
    await ws.authorize_as_user(user_ws.user)

    for messages in await receive_websockets(websockets, [ws]):
        assert not messages


@pytest.mark.asyncio
async def test_disconnection(test_cli, db_users, websockets, ws):
    for user in db_users:
        for user_ws in websockets:
            if user_ws.user == user:
                break
        else:
            break
    else:
        raise Exception("Cannot find offline user")

    await ws.authorize_as_user(user)
    await receive_websockets(websockets)

    await ws.websocket.close(1000)
    await asyncio.sleep(10)

    expected = [PlayerOfflineMessage(ws.user).json()]
    for messages in await receive_websockets(websockets):
        assert messages == expected


@pytest.mark.asyncio
async def test_players_list(test_cli, db_users, websockets, ws):
    user = random.choice(get_offline_users(db_users, websockets))
    await ws.authorize_as_user(user)

    await ws.receive()

    await ws.websocket.send_json({"event": "players.list", "data": ""})

    messages = await ws.receive()

    for websocket in websockets:
        if websocket.user:
            assert PlayerOnlineMessage(websocket.user).json() in messages


@pytest.mark.asyncio
async def test_players_list_with_username(test_cli, db_users, websockets, ws):
    user_ws = random_websocket(websockets)
    user = random.choice(get_offline_users(db_users, websockets))
    await ws.authorize_as_user(user)

    await ws.receive()

    data = user_ws.user.username
    await ws.websocket.send_json({"event": "players.list", "data": data})

    messages = await ws.receive()

    for websocket in websockets:
        if websocket.user:
            message = PlayerOnlineMessage(websocket.user).json()
            if data in websocket.user.username:
                assert message in messages
            else:
                assert message not in messages


@pytest.mark.asyncio
async def test_players_list_with_full_name(test_cli, db_users, websockets, ws):
    user_ws = random_websocket(websockets)
    user = random.choice(get_offline_users(db_users, websockets))
    await ws.authorize_as_user(user)

    await ws.receive()

    data = f"{user_ws.user.first_name} {user_ws.user.last_name}"
    await ws.websocket.send_json({"event": "players.list", "data": data})

    messages = await ws.receive()

    for websocket in websockets:
        if websocket.user:
            message = PlayerOnlineMessage(websocket.user).json()
            if (
                user_ws.user.first_name == websocket.user.first_name
                and user_ws.user.last_name == websocket.user.last_name
            ):
                assert message in messages
            else:
                assert message not in messages
