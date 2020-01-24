import asyncio
import json
from websockets import WebSocketServerProtocol

from typing import Dict, Set, Optional
from config import DATABASE_URI
from explorebaduk.database import create_session
from explorebaduk.models import User, Challenge, Game


db = create_session(DATABASE_URI)

CONNECTED: Set[WebSocketServerProtocol] = set()
USERS: Dict[WebSocketServerProtocol, Optional[User]] = {}
CHALLENGES: Dict[int, Challenge] = {}
GAMES: Dict[int, Game] = {}


def players_event() -> str:
    return f"sync players {json.dumps([str(player) for player in USERS.values() if player])}"


def challenges_event() -> str:
    return f"sync challenges {json.dumps([str(challenge) for challenge in CHALLENGES.values()])}"


async def send_everyone(message: str):
    if USERS:
        await asyncio.gather(*[ws.send(message) for ws in CONNECTED])


async def notify_users():
    if USERS:
        message = players_event()
        await asyncio.gather(*[ws.send(message) for ws in CONNECTED])


async def notify_challenges():
    if USERS:
        message = challenges_event()
        await asyncio.gather(*[ws.send(message) for ws in CONNECTED])


async def register(ws):
    CONNECTED.add(ws)
    await asyncio.gather(ws.send(players_event()), ws.send(challenges_event()))


async def unregister(ws):
    if ws in USERS:
        del USERS[ws]
    CONNECTED.remove(ws)
    await notify_users()
