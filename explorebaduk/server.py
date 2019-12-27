import asyncio
import json
from websockets import WebSocketServerProtocol

from typing import Dict, Tuple
from explorebaduk.config import DATABASE_URI
from explorebaduk.database import create_session
from explorebaduk.models import Player, Challenge, Game


db = create_session(DATABASE_URI)

PLAYERS: Dict[WebSocketServerProtocol, Player] = {}
CHALLENGES: Dict[WebSocketServerProtocol, Challenge] = {}
GAMES: Dict[WebSocketServerProtocol, Game] = {}


def get_by_user_id(user_id: int) -> WebSocketServerProtocol:
    for ws, player in PLAYERS.items():
        if player.logged_in and player.id == user_id:
            return ws


def players_event():
    return json.dumps({
        'type': 'players',
        'data': [player.full_name for player in PLAYERS.values() if
                 player and player.logged_in]
    })


def challenges_event():
    return json.dumps({
        'type': 'challenges',
        'data': [challenge.to_dict() for challenge in CHALLENGES.values()]
    })


async def notify_players():
    if PLAYERS:
        message = players_event()
        await asyncio.gather(*[user.send(message) for user in PLAYERS.keys()])


async def notify_challenges():
    if PLAYERS:
        message = challenges_event()
        await asyncio.gather(*[user.send(message) for user in PLAYERS.keys()])


async def register(ws):
    PLAYERS[ws] = Player(ws)
    await asyncio.gather(ws.send(players_event()),
                         ws.send(challenges_event()))


async def unregister(ws):
    PLAYERS.pop(ws)
    await notify_players()
