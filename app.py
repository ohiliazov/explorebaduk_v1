import websockets
import logging

from explorebaduk.server import register, unregister
from explorebaduk.handlers import handle_message

logger = logging.getLogger('app')


async def start_server(ws: websockets.WebSocketServerProtocol, path: str):
    await register(ws)
    try:
        async for message in ws:
            logger.info(message)
            await handle_message(ws, message)
    finally:
        await unregister(ws)
