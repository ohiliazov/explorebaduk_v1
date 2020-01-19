import asyncio
import json
from websockets import WebSocketServerProtocol

from typing import Dict, Optional
from config import DATABASE_URI
from explorebaduk.database import create_session
from explorebaduk.models import Player, Challenge, Game


db = create_session(DATABASE_URI)

PLAYERS: Dict[WebSocketServerProtocol, Optional[Player]] = {}
CHALLENGES: Dict[int, Challenge] = {}
GAMES: Dict[int, Game] = {}


def players_event() -> str:
    return f"sync players {json.dumps([str(player) for player in PLAYERS.values() if player])}"


def challenges_event() -> str:
    return f"sync challenges {json.dumps([str(challenge) for challenge in CHALLENGES.values()])}"


async def sync_players(message: str):
    if PLAYERS:
        await asyncio.gather(*[ws.send(message) for ws in PLAYERS.keys()])


async def notify_players():
    if PLAYERS:
        message = players_event()
        await asyncio.gather(*[user.send(message) for user in PLAYERS.keys()])


async def notify_challenges():
    if PLAYERS:
        message = challenges_event()
        await asyncio.gather(*[user.send(message) for user in PLAYERS.keys()])


async def register(ws):
    PLAYERS[ws] = None
    await asyncio.gather(ws.send(players_event()), ws.send(challenges_event()))


async def unregister(ws):
    del PLAYERS[ws]
    await notify_players()
