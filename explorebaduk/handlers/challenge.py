import asyncio
import logging

from explorebaduk.constants import ChallengeAction
from explorebaduk.exceptions import InvalidMessageError
from explorebaduk.models import Challenge
from explorebaduk.server import USERS, CHALLENGES, send_everyone
from explorebaduk.schema import NewChallengeSchema

logger = logging.getLogger("challenge_handler")


CHALLENGE_CREATED = "OK challenge new: created {}"
NOT_LOGGED_IN = "ERROR challenge new: not logged in"

CHALLENGE_CANCEL = "OK challenge cancel: cancelled {}"
CANCEL_NOT_FOUND = "ERROR challenge cancel: not found"

CHALLENGE_JOINED = "OK challenge joined: joined {}"
JOIN_NOT_FOUND = "ERROR challenge join: not found"
JOIN_NOT_ALLOWED = "ERROR challenge join: not allowed"

CHALLENGE_JOINED_SYNC = "sync challenge {} {} {}"


async def sync_add_challenge(challenge: Challenge):
    return await send_everyone(f"SYNC challenge add {challenge}")


async def sync_del_challenge(challenge: Challenge):
    return await send_everyone(f"SYNC challenge del {challenge}")


def next_id_gen():
    next_id = 0

    while True:
        next_id += 1
        yield next_id


id_gen = next_id_gen()


async def create_challenge(ws, data):
    logger.info("create_challenge")
    player = USERS[ws]

    if not player:
        return await ws.send(NOT_LOGGED_IN)

    data = NewChallengeSchema().load(data)

    challenge_id = next(id_gen)
    challenge = Challenge(challenge_id, player, data)
    CHALLENGES[challenge_id] = challenge

    return await asyncio.gather(ws.send(CHALLENGE_CREATED.format(challenge_id)), sync_add_challenge(challenge))


async def cancel_challenge(ws, data: dict):
    logger.info("cancel_challenge")

    challenge_id = int(data["challenge_id"])
    challenge = CHALLENGES.get(challenge_id)

    if challenge_id not in CHALLENGES:
        return await ws.send(CANCEL_NOT_FOUND)

    CHALLENGES.pop(ws)

    message = CHALLENGE_CANCEL.format(challenge_id)
    return await challenge.send_all(message)


async def join_challenge(ws, data):
    challenge_id = int(data["challenge_id"])
    player = USERS[ws]

    challenge = CHALLENGES.get(challenge_id)
    if not challenge:
        return await ws.send(JOIN_NOT_FOUND)

    if player in challenge.blacklist:
        return await ws.send(JOIN_NOT_ALLOWED)

    is_ready = challenge.join_player(player, challenge.data)
    message = CHALLENGE_JOINED.format(challenge_id)
    sync_message = CHALLENGE_JOINED_SYNC.format(challenge_id, int(is_ready), challenge)

    return await asyncio.gather(ws.send(message), challenge.send_all(sync_message))


def accept_challenge(ws, data):
    pass


def decline_challenge(ws, data):
    pass


def revise_challenge(ws, data):
    pass


async def handle_challenge(ws, data: dict):
    logger.info("handle_challenge")

    player = USERS[ws]

    if not player:
        return ws.send(NOT_LOGGED_IN)

    action = ChallengeAction(data.pop("action"))
    if action is ChallengeAction.NEW:
        await create_challenge(ws, data)

    elif action is ChallengeAction.CANCEL:
        await cancel_challenge(ws, data)

    elif action is ChallengeAction.JOIN:
        await join_challenge(ws, data)

    else:
        raise InvalidMessageError(f"ERROR challenge {action}: not implemented")
