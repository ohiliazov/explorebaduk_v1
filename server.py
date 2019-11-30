import asyncio
import json
import logging

import websockets

import config

from handlers import handle_message
from database import DatabaseWrapper


logging.getLogger('websockets').setLevel(logging.ERROR)
db = DatabaseWrapper(config.DATABASE_URI)

CONNECTED = {}


def online_players():
    message = {
        "type": "players",
        "action": "get",
        "payload": [player for player in CONNECTED.values() if player]
    }
    return json.dumps(message)


async def notify_players():
    if CONNECTED:
        message = online_players()
        await asyncio.wait([player.send(message) for player in CONNECTED])


async def register(websocket: websockets.WebSocketServerProtocol):
    host, port = websocket.remote_address[:2]
    print(f'Connected: host_addr={host} port={port}')
    CONNECTED[websocket] = None


async def unregister(websocket: websockets.WebSocketServerProtocol):
    host, port = websocket.remote_address[:2]
    print(f'Disconnected: host_addr={host} port={port}')
    del CONNECTED[websocket]


async def eb_server(websocket: websockets.WebSocketServerProtocol, path: str):
    await register(websocket)
    try:
        async for message in websocket:
            print(message)
            await handle_message(websocket, message)
    finally:
        await unregister(websocket)


if __name__ == '__main__':
    start_server = websockets.serve(eb_server, config.SERVER_HOST, config.SERVER_PORT)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
