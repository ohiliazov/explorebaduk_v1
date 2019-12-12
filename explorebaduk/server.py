import asyncio
import json
from websockets import WebSocketServerProtocol

from typing import Dict
from explorebaduk.config import DATABASE_URI
from explorebaduk.database import create_session
from explorebaduk.models import Player, Challenge, Game


db = create_session(DATABASE_URI)


class GameServer:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not GameServer.__instance:
            GameServer.__instance = super(GameServer, cls).__new__(cls, *args, **kwargs)
        return GameServer.__instance

    players: Dict[WebSocketServerProtocol, Player] = {}
    challenges: Dict[WebSocketServerProtocol, Challenge] = {}
    games: Dict[WebSocketServerProtocol, Game] = {}

    @classmethod
    def players_event(cls):
        return json.dumps({
            'type': 'players',
            'data': [player.user.full_name for player in cls.players.values() if player and player.logged_in]
        })

    @classmethod
    async def notify_players(cls):
        if cls.players:
            message = cls.players_event()
            await asyncio.gather(*[user.send(message) for user in cls.players.keys()])

    @classmethod
    async def register(cls, ws):
        cls.players[ws] = Player()
        await cls.notify_players()

    @classmethod
    async def unregister(cls, ws):
        cls.players.pop(ws)
        await cls.notify_players()
