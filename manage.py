import asyncio
import websockets
import logging
from functools import partial

from config import get_config
from app import start_server
from explorebaduk.database import DatabaseHandler


FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt=DATE_FORMAT)

if __name__ == "__main__":
    config = get_config()
    loop = asyncio.get_event_loop()

    db_handler = DatabaseHandler(config["database_uri"])

    server = websockets.serve(
        ws_handler=partial(start_server, db_handler=db_handler),
        host=config["server_host"],
        port=config["server_port"],
        loop=loop,
    )

    loop.run_until_complete(server)
    loop.run_forever()
