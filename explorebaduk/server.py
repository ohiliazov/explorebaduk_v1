import asyncio

from explorebaduk.config import DATABASE_URI
from explorebaduk.database import create_session


class GameServer:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not GameServer.__instance:
            GameServer.__instance = super(GameServer, cls).__new__(cls, *args, **kwargs)
        return GameServer.__instance

    ws_server = None
    users = {}
    challenges = {}
    games = {}

    def __init__(self):
        self.sync_queue = asyncio.Queue()
        self.session = create_session(DATABASE_URI)

    def add_ws_server(self, ws_server):
        self.ws_server = ws_server

    @property
    def clients(self):
        if self.ws_server:
            return self.ws_server.websockets

    async def sync_user(self, ws):
        message = {
            "action": "sync",
            "data": {
                "users": [user.as_dict() for user in self.users],
                "games": self.games,
                "challenges": self.challenges,
            }
        }
        self.sync_queue.put_nowait((ws, message))

    async def goodbye_user(self, ws):
        self.users.pop(ws, None)

    def sync_all_users(self, ws, data: dict):
        self.sync_queue.put_nowait((ws, data))


eb_server = GameServer()
