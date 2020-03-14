import asyncio

from explorebaduk.exceptions import MessageHandlerError
from explorebaduk.helpers import get_challenge_by_id, send_sync_messages
from explorebaduk.models import Challenge
from explorebaduk.server import PLAYERS, CHALLENGES


async def handle_challenge_new(ws, data):
    """Create new challenge"""
    player = PLAYERS.get(ws)

    if not player:
        raise MessageHandlerError("not logged in")

    if get_challenge_by_id(player.id):
        raise MessageHandlerError("already created")

    challenge = Challenge(player, data)

    CHALLENGES.add(challenge)

    await asyncio.gather(ws.send(f"OK [challenge new] {challenge}"), send_sync_messages(f"challenges add {challenge}"))


async def handle_challenge_cancel(ws, data: dict):
    """Cancel challenge"""
    player = PLAYERS.get(ws)

    if not player:
        raise MessageHandlerError("not logged in")

    challenge = get_challenge_by_id(player.id)

    if not challenge:
        raise MessageHandlerError("not found")

    CHALLENGES.remove(challenge)

    await asyncio.gather(
        ws.send(f"OK [challenge cancel] {challenge}"), send_sync_messages(f"sync challenge removed {challenge}")
    )


async def handle_challenge_join(ws, data):
    """Join challenge"""
    player = PLAYERS.get(ws)

    if not player:
        raise MessageHandlerError("not logged in")

    challenge = get_challenge_by_id(data["challenge_id"])

    if not challenge:
        raise MessageHandlerError("not found")

    if player is challenge.creator:
        raise MessageHandlerError("self join attempt")

    if player in challenge.pending:
        raise MessageHandlerError("already joined")

    await challenge.add_player(player)

    await asyncio.gather(
        ws.send(f"OK [challenge join] {challenge}"), challenge.creator.send(f"challenge joined {player}")
    )


async def handle_challenge_leave(ws, data):
    """Leave challenge"""
    player = PLAYERS.get(ws)

    if not player:
        raise MessageHandlerError("not logged in")

    challenge = get_challenge_by_id(data["challenge_id"])

    if not challenge:
        raise MessageHandlerError("not found")

    if player is challenge.creator:
        raise MessageHandlerError("self join attempt")

    if player not in challenge.pending:
        raise MessageHandlerError("not joined")

    await challenge.remove_player(player)

    await asyncio.gather(
        ws.send(f"OK [challenge leave] {challenge}"), challenge.creator.send(f"challenge left {player}")
    )
