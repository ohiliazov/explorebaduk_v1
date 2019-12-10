import asyncio
import json

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

    @staticmethod
    async def send_message(ws, action, data: dict):
        message = {
            "action": action,
            "data": data,
        }
        await ws.send(json.dumps(message))

    async def sync_user(self, ws):
        data = {
            "users": [user.as_dict() for user in self.users],
            "games": self.games,
            "challenges": self.challenges,
        }

        await self.send_message(ws, "sync", data)

    async def goodbye_user(self, ws):
        self.users.pop(ws, None)

    async def sync_all_users(self, data: dict):
        message = {
            "action": "sync",
            "data": data,
        }
        await self.sync_queue.put(message)


eb_server = GameServer()
