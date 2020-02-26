import websockets
import logging

from explorebaduk.message import handle_message
from explorebaduk.handlers.sync import register, unregister

logger = logging.getLogger("app")


async def start_server(ws: websockets.WebSocketServerProtocol, path: str):
    await register(ws)
    try:
        async for message in ws:
            await handle_message(ws, message)
    finally:
        await unregister(ws)
