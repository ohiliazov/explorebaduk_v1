import asyncio
import json

from explorebaduk.config import DATABASE_URI
from explorebaduk.database import create_session
from explorebaduk.models import Player


class GameServer:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not GameServer.__instance:
            GameServer.__instance = super(GameServer, cls).__new__(cls, *args, **kwargs)
        return GameServer.__instance

    users = {}
    challenges = {}
    games = {}

    def __init__(self):
        self.session = create_session(DATABASE_URI)

    def players_event(self):
        return json.dumps({
            'type': 'players',
            'data': [player.user.full_name for player in self.users.values() if player.logged_in]
        })

    async def notify_users(self):
        if self.users:
            message = self.players_event()
            await asyncio.gather(*[user.send(message) for user in self.users.keys()])

    async def register(self, ws):
        self.users[ws] = Player()
        await self.notify_users()

    async def unregister(self, ws):
        self.users.pop(ws)
        await self.notify_users()


eb_server = GameServer()
