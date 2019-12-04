import logging

import config
from database import create_session
from server import GameServer

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('websockets').setLevel(logging.ERROR)

if __name__ == '__main__':
    session = create_session(config.DATABASE_URI)

    game_server = GameServer(config.SERVER_HOST, config.SERVER_PORT, config.DATABASE_URI)
    game_server.serve()
