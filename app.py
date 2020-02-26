import websockets
import logging

from explorebaduk.handlers import handle_message_v2
from explorebaduk.handlers.sync import register, unregister

logger = logging.getLogger("app")


async def start_server(ws: websockets.WebSocketServerProtocol, path: str):
    await register(ws)
    try:
        async for message in ws:
            logger.info(message)
            await handle_message_v2(ws, message)
    finally:
        await unregister(ws)
