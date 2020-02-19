import asyncio
import logging

from explorebaduk.constants import ChallengeAction
from explorebaduk.exceptions import InvalidMessageError
from explorebaduk.models import Player, Challenge
from explorebaduk.server import CONNECTED, PLAYERS, CHALLENGES
from explorebaduk.schema import ChallengeSchema, PlayerRequestSchema

from explorebaduk.helpers import send_messages, send_sync_messages, error_message

logger = logging.getLogger("challenge_handler")

NEXT_CHALLENGE_ID = 0


def challenge_error(action, reason):
    return error_message("challenge", action, reason)


def challenge_created(challenge: Challenge) -> str:
    return f"sync challenge created {challenge}"


def challenge_removed(challenge: Challenge) -> str:
    return f"sync challenge removed {challenge}"


def notify_player_joined(challenge: Challenge, player: Player) -> str:
    return f"challenge {challenge} joined {str(player)}"


def next_challenge_id():
    global NEXT_CHALLENGE_ID
    NEXT_CHALLENGE_ID += 1
    return NEXT_CHALLENGE_ID


async def create_challenge(ws, data):
    logger.info("create_challenge")
    player = PLAYERS[ws]

    if not player:
        return await ws.send(challenge_error("new", "not logged in"))

    data = ChallengeSchema().load(data)

    challenge_id = next_challenge_id()
    challenge = Challenge(challenge_id, player, data)

    message = challenge_created(challenge)
    CHALLENGES[challenge_id] = challenge

    return await send_sync_messages(message)


async def cancel_challenge(ws, data: dict):
    logger.info("cancel_challenge")

    challenge_id = int(data["challenge_id"])
    challenge = CHALLENGES.get(challenge_id)

    if challenge_id not in CHALLENGES:
        return await ws.send(challenge_error("cancel", "not found"))

    del CHALLENGES[challenge_id]

    message = challenge_removed(challenge)
    return await send_sync_messages(message)


async def join_challenge(ws, data):
    logger.info("join_challenge")
    challenge_id = int(data["challenge_id"])
    player = PLAYERS[ws]

    challenge = CHALLENGES.get(challenge_id)
    if not challenge:
        return await ws.send(challenge_error("join", "not found"))

    data = PlayerRequestSchema().load(data)

    if player in challenge.pending:
        return await ws.send(challenge_error("join", "already joined"))

    player_request = challenge.join_player(player, data)

    message_to_joined = f"challenge join OK {challenge}"
    message_to_creator = f"challenge joined {player_request}"

    return await asyncio.gather(
        player.send(message_to_joined),
        challenge.creator.send(message_to_creator)
    )


async def handle_challenge(ws, data: dict):
    logger.info("handle_challenge")

    player = PLAYERS[ws]
    action = ChallengeAction(data.pop("action"))

    if not player:
        return ws.send(challenge_error(action, "not logged in"))

    if action is ChallengeAction.NEW:
        await create_challenge(ws, data)

    elif action is ChallengeAction.CANCEL:
        await cancel_challenge(ws, data)

    elif action is ChallengeAction.JOIN:
        await join_challenge(ws, data)

    else:
        raise InvalidMessageError(f"ERROR challenge {action}: not implemented")
