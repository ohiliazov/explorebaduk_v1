import asyncio
import logging

from explorebaduk.models import Player, Challenge, Game
from explorebaduk.server import PLAYERS, CHALLENGES
from explorebaduk.schema import (
    ChallengeNewSchema,
    ChallengeIdSchema,
    ChallengeStartSchema,
)

from explorebaduk.helpers import send_sync_messages, error_message, get_player_by_id

logger = logging.getLogger("challenge_handler")

NEXT_CHALLENGE_ID = 0
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


def next_challenge_id():
    global NEXT_CHALLENGE_ID
    NEXT_CHALLENGE_ID += 1
    return NEXT_CHALLENGE_ID


def next_game_id():
    global NEXT_GAME_ID
    NEXT_GAME_ID += 1
    return NEXT_GAME_ID


async def handle_challenge_new(ws, data):
    """Create new challenge"""
    player = PLAYERS[ws]

    if not player:
        return await ws.send(challenge_error("new", "not logged in"))

    challenge_id = next_challenge_id()
    challenge = Challenge(challenge_id, player, data)

    message = challenge_created(challenge)
    CHALLENGES[challenge_id] = challenge

    return await send_sync_messages(message)


async def handle_challenge_cancel(ws, data: dict):
    """Cancel challenge"""

    challenge_id = data["challenge_id"]
    challenge = CHALLENGES.get(challenge_id)

    if challenge:
        return await ws.send(challenge_error("cancel", "not found"))

    del CHALLENGES[challenge_id]

    message = challenge_removed(challenge)
    return await send_sync_messages(message)


async def handle_challenge_join(ws, data):
    """Join challenge"""

    challenge_id = data["challenge_id"]

    challenge = CHALLENGES.get(challenge_id)
    if not challenge:
        return await ws.send(challenge_error("join", "not found"))

    player = PLAYERS[ws]

    if player == challenge.creator:
        return await ws.send(challenge_error("join", "self join attempt"))

    if player in challenge.pending:
        return await ws.send(challenge_error("join", "already joined"))

    player_request = challenge.join_player(player, data)

    message_to_joined = f"challenge join OK {challenge_id}"
    message_to_creator = f"challenge joined {player_request}"

    return await asyncio.gather(player.send(message_to_joined), challenge.creator.send(message_to_creator))


async def handle_challenge_leave(ws, data):
    """Leave challenge"""

    challenge_id = data["challenge_id"]

    if ws not in PLAYERS:
        return await ws.send(challenge_error("leave", "not logged in"))

    player = PLAYERS[ws]

    challenge = CHALLENGES.get(challenge_id)
    if not challenge:
        return await ws.send(challenge_error("leave", "not found"))

    if player == challenge.creator:
        return await ws.send(challenge_error("leave", "self leave attempt"))

    if player not in challenge.pending:
        return await ws.send(challenge_error("leave", "not joined"))

    player_request = challenge.leave_player(player)

    message_to_joined = f"challenge leave OK {challenge_id}"
    message_to_creator = f"challenge left {player_request}"

    return await asyncio.gather(player.send(message_to_joined), challenge.creator.send(message_to_creator))


async def handle_challenge_start(ws, data: dict):
    """Start game from challenge"""

    challenge_id = data["challenge_id"]
    challenge = CHALLENGES.get(challenge_id)

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

    await asyncio.gather(
        creator.send(f"challenge start {challenge_id}"),
        opponent.send(f"challenge start {challenge_id}"),
        send_sync_messages(challenge_started(game)),
    )

    del CHALLENGES[challenge_id]
