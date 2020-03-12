import asyncio
import logging

from explorebaduk.models import Player, Challenge, Game
from explorebaduk.server import PLAYERS, CHALLENGES
from explorebaduk.helpers import send_sync_messages, error_message, get_player_by_id, get_challenge_by_id

logger = logging.getLogger("challenge_handler")

NEXT_GAME_ID = 0  # TODO: get ID from database


def challenge_error(action, reason):
    return error_message("challenge", action, reason)


def challenge_created(challenge: Challenge) -> str:
    return f"sync challenge created {challenge}"


def challenge_removed(challenge: Challenge) -> str:
    return f"sync challenge removed {challenge}"


def challenge_started(game: Game) -> str:
    return f"sync challenge started {game}"


def notify_player_joined(challenge: Challenge, player: Player) -> str:
    return f"challenge {challenge} joined {str(player)}"


def next_game_id():
    global NEXT_GAME_ID
    NEXT_GAME_ID += 1
    return NEXT_GAME_ID


async def handle_challenge_new(ws, data):
    """Create new challenge"""
    player = PLAYERS[ws]

    if not player:
        return await ws.send(challenge_error("new", "not logged in"))

    if get_challenge_by_id(player.id):
        return await ws.send(challenge_error("new", "already exists"))

    challenge = Challenge(player.id, player, data)

    CHALLENGES.add(challenge)

    return await send_sync_messages(challenge_created(challenge))


async def handle_challenge_cancel(ws, data: dict):
    """Cancel challenge"""

    challenge_id = data["challenge_id"]
    challenge = get_challenge_by_id(challenge_id)

    if not challenge:
        return await ws.send(challenge_error("cancel", "not found"))

    CHALLENGES.remove(challenge)

    message = challenge_removed(challenge)
    return await send_sync_messages(message)


async def handle_challenge_join(ws, data):
    """Join challenge"""

    challenge_id = data["challenge_id"]

    challenge = get_challenge_by_id(challenge_id)
    if not challenge:
        return await ws.send(challenge_error("join", "not found"))

    player = PLAYERS[ws]

    if player == challenge.creator:
        return await ws.send(challenge_error("join", "self join attempt"))

    if player in challenge.pending:
        return await ws.send(challenge_error("join", "already joined"))

    await challenge.add_player(player)

    return await ws.send(f"challenge join OK {challenge_id}")


async def handle_challenge_leave(ws, data):
    """Leave challenge"""

    challenge_id = data["challenge_id"]

    if ws not in PLAYERS:
        return await ws.send(challenge_error("leave", "not logged in"))

    player = PLAYERS[ws]

    challenge = get_challenge_by_id(challenge_id)
    if not challenge:
        return await ws.send(challenge_error("leave", "not found"))

    if player == challenge.creator:
        return await ws.send(challenge_error("leave", "self leave attempt"))

    if player not in challenge.pending:
        return await ws.send(challenge_error("leave", "not joined"))

    await challenge.remove_player(player)

    return await ws.send(f"challenge leave OK {challenge_id}")


async def handle_challenge_start(ws, data: dict):
    """Start game from challenge"""

    challenge_id = data["challenge_id"]
    challenge = get_challenge_by_id(challenge_id)

    # challenge should exist
    if not challenge:
        return await ws.send(challenge_error("start", "not found"))

    # only creator can start the game
    creator = challenge.creator
    if ws is not creator.ws:
        return await ws.send(challenge_error("start", "not creator"))

    opponent_id = data["opponent_id"]
    opponent = get_player_by_id(opponent_id)

    # opponent should be online
    if not opponent:
        return await ws.send("Opponent not found")

    # opponent should be in pending
    if opponent not in challenge.pending:
        return await ws.send("Opponent not in pending")

    # TODO: implement
    game_id = next_game_id()
    game = Game.from_challenge(game_id, challenge, opponent)
    game.black.start_timer()

    CHALLENGES.remove(challenge)

    creator_color = "black" if game.black.player is creator else "white"
    opponent_color = "black" if game.black.player is opponent else "white"

    await asyncio.gather(
        creator.send(f"challenge start {challenge_id} {creator_color}"),
        opponent.send(f"challenge start {challenge_id} {opponent_color}"),
        send_sync_messages(challenge_started(game)),
    )
