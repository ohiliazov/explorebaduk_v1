import logging

import config
from database import create_session
from server import GameServer


def setup_logger():
    logging.getLogger('websockets').setLevel(logging.ERROR)
    FORMAT = "%(asctime)s [%(module)s %(funcName)s] %(levelname)s: %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt=DATE_FORMAT)


if __name__ == '__main__':
    setup_logger()
    session = create_session(config.DATABASE_URI)

    game_server = GameServer(config.SERVER_HOST, config.SERVER_PORT, config.DATABASE_URI)
    game_server.serve()
