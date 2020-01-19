import asyncio
import websockets
import logging

import config
from explorebaduk.server import register, unregister
from explorebaduk.handlers import handle_message


FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt=DATE_FORMAT)
logger = logging.getLogger("explorebaduk")


async def start_server(ws: websockets.WebSocketServerProtocol, path: str):
    await register(ws)
    try:
        async for message in ws:
            logger.info(message)
            await handle_message(ws, message)
    finally:
        await unregister(ws)


loop = asyncio.get_event_loop()

server = websockets.serve(start_server, config.SERVER_HOST, config.SERVER_PORT, loop=loop)

loop.run_until_complete(server)
loop.run_forever()
