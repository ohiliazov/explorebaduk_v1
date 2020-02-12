import asyncio
import websockets
import logging

import config
from app import start_server

FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt=DATE_FORMAT)

loop = asyncio.get_event_loop()

server = websockets.serve(start_server, config.SERVER_HOST, config.SERVER_PORT, loop=loop)

loop.run_until_complete(server)
loop.run_forever()
