import asyncio
import logging
import json

from explorebaduk.constants import (
    CREATE_CHALLENGE,
    CANCEL_CHALLENGE,
    JOIN_CHALLENGE,
    CHALLENGE, OK, ERROR
)
from explorebaduk.exceptions import AuthenticationError, InvalidMessageError
from explorebaduk.models import Challenge
from explorebaduk.server import PLAYERS, CHALLENGES, notify_challenges
from explorebaduk.schema import ChallengeSchema

logger = logging.getLogger('challenge_handler')


class ChallengeError(Exception):
    pass


def challenge_ok_event(message: str):
    return json.dumps({'type': CHALLENGE, 'result': OK, 'message': message})


def challenge_error_event(error_message: str):
    return json.dumps({'type': CHALLENGE, 'result': ERROR, 'message': error_message})


async def create_challenge(ws, data):
    if ws in CHALLENGES:
        return await ws.send(challenge_error_event('Challenge already exists'))

    data = ChallengeSchema().load(data)
    player = PLAYERS[ws]

    CHALLENGES[player.id] = Challenge(player, data)
    logger.info('Challenge created by: %s', PLAYERS[ws].user.full_name)
    return await asyncio.gather(ws.send(challenge_ok_event('created')), notify_challenges())


async def cancel_challenge(ws):
    logger.info("Cancelling challenge")

    if ws not in CHALLENGES:
        return await ws.send(challenge_error_event('Challenge not exists'))

    challenge = CHALLENGES.pop(ws)

    return await asyncio.gather(*[player.send(challenge_ok_event('cancelled')) for player in challenge.joined])


async def join_challenge(ws, data):
    data = ChallengeSchema().load(data)

    if not data['challenge_id']:
        return await ws.send(challenge_error_event('Challenge ID is not provided'))

    player = PLAYERS[ws]
    pass


def accept_challenge(ws, data):
    pass


def decline_challenge(ws, data):
    pass


def revise_challenge(ws, data):
    pass


async def handle_challenge(ws, action: str, data: dict):
    player = PLAYERS[ws]
    if not player.logged_in:
        raise AuthenticationError("Player not logged in")

    if action == CREATE_CHALLENGE:
        await create_challenge(ws, data)

    elif action == CANCEL_CHALLENGE:
        await cancel_challenge(ws)

    elif action == JOIN_CHALLENGE:
        await join_challenge(ws, data)

    else:
        raise InvalidMessageError(f"Invalid action: {action}")
