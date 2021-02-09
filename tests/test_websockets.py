import pytest

from .helpers import receive_messages


@pytest.mark.asyncio
async def test_authorize_as_guest(test_cli, guest_websockets, websocket):
    websocket.send_json({})
    messages = receive_messages(websocket)

    assert {"event": "whoami", "data": None} in messages
    assert {"event": "players.list", "data": []} in messages


@pytest.mark.asyncio
async def test_authorize_as_user(test_cli, guest_websockets, websocket):
    websocket.send_json({})
    messages = receive_messages(websocket)

    assert {"event": "whoami", "data": None} in messages
    assert {"event": "players.list", "data": []} in messages
