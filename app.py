import websockets
import logging

from explorebaduk.handlers import handle_message, register, unregister

logger = logging.getLogger("app")


async def start_server(ws: websockets.WebSocketServerProtocol, path: str, db_handler):
    print("here")
    await register(ws)
    try:
        async for message in ws:
            await handle_message(ws, message, db_handler)
    finally:
        await unregister(ws)
