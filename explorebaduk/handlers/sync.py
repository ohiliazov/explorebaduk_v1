import asyncio
import json

from typing import List
from explorebaduk.server import CONNECTED, PLAYERS, CHALLENGES
from explorebaduk.handlers.auth import player_joined, player_left
from explorebaduk.handlers.challenge import challenge_created
from explorebaduk.helpers import send_messages, send_sync_messages


def all_players() -> List[str]:
    return [player_joined(player) for player in PLAYERS.values()]


def all_challenges() -> List[str]:
    return [challenge_created(challenge) for challenge in CHALLENGES.values()]


async def register(ws):
    CONNECTED.add(ws)

    messages = all_players() + all_challenges()

    if messages:
        await send_messages(ws, messages)


async def unregister(ws):
    if ws in PLAYERS:
        player = PLAYERS[ws]
        del PLAYERS[ws]
        await send_sync_messages([player_left(player)])

    CONNECTED.remove(ws)
