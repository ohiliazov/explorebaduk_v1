import asyncio
import random

import pytest

from explorebaduk.messages import (
    GameInvitesMessage,
    OpenGamesMessage,
    PlayerListMessage,
    PlayerOfflineMessage,
    WhoAmIMessage,
)

from .helpers import (
    get_offline_users,
    get_online_users,
    random_websocket,
    receive_websockets,
)


@pytest.mark.asyncio
async def test_authorize_as_guest(test_cli, websockets, ws):
    await ws.authorize_as_guest()

    messages = await ws.receive()

    assert len(messages) == 3
    assert WhoAmIMessage(None).json() in messages

    players_list = PlayerListMessage(get_online_users(websockets)).json()
    assert players_list in messages

    assert OpenGamesMessage({}).json() in messages


@pytest.mark.asyncio
async def test_authorize_as_user(test_cli, db_users, websockets, ws):
    user = random.choice(get_offline_users(db_users, websockets))
    await ws.authorize_as_user(user)

    messages = await ws.receive()

    assert len(messages) == 4
    assert WhoAmIMessage(user).json() in messages

    players_list = PlayerListMessage(get_online_users(websockets, [user])).json()
    assert players_list in messages

    assert OpenGamesMessage({}).json() in messages
    assert GameInvitesMessage({}).json() in messages


@pytest.mark.asyncio
async def test_refresh_as_user(test_cli, db_users, websockets, ws):
    user = random.choice(get_offline_users(db_users, websockets))
    await ws.authorize_as_user(user)
    await ws.receive()

    await ws.refresh()

    messages = await ws.receive()

    assert len(messages) == 3

    players_list = PlayerListMessage(get_online_users(websockets, [user])).json()
    assert players_list in messages

    assert OpenGamesMessage({}).json() in messages
    assert GameInvitesMessage({}).json() in messages


@pytest.mark.asyncio
async def test_refresh_as_guest(test_cli, websockets, ws):
    await ws.authorize_as_guest()
    await ws.receive()

    await ws.refresh()

    messages = await ws.receive()

    assert len(messages) == 2

    players_list = PlayerListMessage(get_online_users(websockets)).json()
    assert players_list in messages

    assert OpenGamesMessage({}).json() in messages


@pytest.mark.asyncio
async def test_interrupted_connection(test_cli, db_users, websockets, ws):
    user_ws = random_websocket(websockets)

    await user_ws.websocket.close(1000)

    await ws.authorize_as_user(user_ws.user)

    for messages in await receive_websockets(websockets):
        assert not messages


@pytest.mark.asyncio
async def test_disconnection(test_cli, db_users, websockets, ws):
    user_ws = random_websocket(websockets)

    await user_ws.websocket.close()
    await asyncio.sleep(10)

    expected = [PlayerOfflineMessage(user_ws.user).json()]
    for messages in await receive_websockets(websockets, [user_ws]):
        assert messages == expected
