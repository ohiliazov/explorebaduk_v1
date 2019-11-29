import asyncio
import json
import logging

import websockets

from constants import Action
from schema import LoginPayload

logging.getLogger('websockets').setLevel(logging.ERROR)
CONNECTED = {}


def players_online():
    return json.dumps({"players": [player for player in CONNECTED.values() if player]})


async def notify_players():
    if CONNECTED:
        message = players_online()
        await asyncio.wait([player.send(message) for player in CONNECTED])


async def register(websocket: websockets.WebSocketClientProtocol):
    host, port = websocket.remote_address[:2]
    print(f'Connected: host_addr={host} port={port}')
    CONNECTED[websocket] = None


async def unregister(websocket):
    host, port = websocket.remote_address[:2]
    print(f'Disconnected: host_addr={host} port={port}')
    del CONNECTED[websocket]


async def handle_login(websocket, data):
    if CONNECTED[websocket]:
        return await websocket.send(
            json.dumps({"status": "success", "message": f"Already logged in"}))

    errors = LoginPayload().validate(data)

    if errors:
        return await websocket.send(json.dumps({"status": "failure", "message": errors}))

    username = data['username']
    CONNECTED[websocket] = username
    await websocket.send(json.dumps({"status": "success", "message": f"Logged in as {username}"}))
    await notify_players()


async def handle_chat(websocket, data):
    pass


async def handle_challenge(websocket, data):
    pass


async def consume_message(websocket, message):
    data = json.loads(message)
    action = Action(data['action'])

    if action == Action.LOGIN:
        await handle_login(websocket, data)

    elif action == Action.CHAT:
        await handle_chat(websocket, data)

    elif action == Action.CHALLENGE:
        await handle_challenge(websocket, data)


async def eb_server(websocket: websockets.WebSocketClientProtocol, path):
    await register(websocket)
    try:
        async for message in websocket:
            await consume_message(websocket, message)
    finally:
        await unregister(websocket)


if __name__ == '__main__':
    start_server = websockets.serve(eb_server, "localhost", 8080)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
