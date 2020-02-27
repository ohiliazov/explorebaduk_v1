import websockets
import logging

from explorebaduk.handlers import handle_message, register, unregister

logger = logging.getLogger("app")


async def start_server(ws: websockets.WebSocketServerProtocol, path: str):
    await register(ws)
    try:
        async for message in ws:
            await handle_message(ws, message)
    finally:
        await unregister(ws)
