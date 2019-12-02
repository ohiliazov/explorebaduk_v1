import logging

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

import config
from server import GameServer

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('websockets').setLevel(logging.ERROR)


if __name__ == '__main__':
    engine = create_engine(config.DATABASE_URI)
    session = sessionmaker()(bind=engine)

    game_server = GameServer(config.SERVER_HOST, config.SERVER_PORT, session)
    game_server.serve()
