import logging

import config


logging.basicConfig(level=logging.DEBUG)
logging.getLogger('websockets').setLevel(logging.ERROR)


if __name__ == '__main__':
    from server import GameServer

    eb_server = GameServer(config.SERVER_HOST,
                           config.SERVER_PORT,
                           config.DATABASE_URI)
    eb_server.serve()
