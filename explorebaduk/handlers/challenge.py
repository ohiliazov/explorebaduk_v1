import asyncio

from explorebaduk.models import Game, Challenge
from explorebaduk.server import PLAYERS, CHALLENGES
from explorebaduk.helpers import get_challenge_by_id, send_sync_messages
from explorebaduk.exceptions import MessageHandlerError


async def handle_challenge_new(ws, data, db_handler):
    """Create new challenge"""
    player = PLAYERS.get(ws)

    if not player:
        raise MessageHandlerError("not logged in")

    if get_challenge_by_id(player.id):
        raise MessageHandlerError("already created")

    game = Game(data, db_handler)
    challenge = Challenge(player.id, player, game)

    CHALLENGES.add(challenge)

    await asyncio.gather(ws.send(f"OK [challenge new] {challenge}"), send_sync_messages(f"challenges add {challenge}"))


async def handle_challenge_cancel(ws, data: dict, db_handler):
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


async def handle_challenge_join(ws, data, db_handler):
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


async def handle_challenge_leave(ws, data, db_handler):
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
