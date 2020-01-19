import asyncio
import logging
import json

from explorebaduk.constants import (
    NEW_CHALLENGE,
    CANCEL_CHALLENGE,
    JOIN_CHALLENGE,
    CHALLENGE,
    ERROR,
)
from explorebaduk.exceptions import AuthenticationError, InvalidMessageError
from explorebaduk.models import Challenge, Player
from explorebaduk.server import PLAYERS, CHALLENGES, notify_challenges
from explorebaduk.schema import NewChallengeSchema

logger = logging.getLogger("challenge_handler")


CHALLENGE_CREATED = 'OK challenge new: created'
NOT_LOGGED_IN = 'ERROR challenge new: not logged in'

CHALLENGE_CANCEL = 'OK challenge cancel: cancelled'


def sync_add_challenge(challenge: Challenge):
    message = f'SYNC challenge add {challenge}'
    return await asyncio.gather(message)


def sync_del_challenge(challenge: Challenge):
    return f'SYNC challenge del {challenge}'


def next_id_gen():
    next_id = 0

    while True:
        next_id += 1
        yield next_id


id_gen = next_id_gen()


def challenge_response(status: str, action: str, message: str = ''):
    return f"{status} challenge {action} {message}"


def challenge_join_event(challenge: Challenge, player: Player, data: dict):
    return json.dumps(
        {
            "type": CHALLENGE,
            "action": JOIN_CHALLENGE,
            "challenge_id": challenge.id,
            "player": player.to_dict(),
            "data": data,
        }
    )


def challenge_error_event(error_message: str):
    return json.dumps({"type": CHALLENGE, "result": ERROR, "message": error_message})


async def create_challenge(ws, data):
    player = PLAYERS[ws]

    if not player:
        return await ws.send(NOT_LOGGED_IN)

    data = NewChallengeSchema().load(data)

    challenge_id = next(id_gen)
    CHALLENGES[challenge_id] = Challenge(challenge_id, player, data)
    logger.info('Challenge created by: %s', PLAYERS[ws].user.full_name)
    return await asyncio.gather(ws.send(f"OK challenge new {next(id_gen)}"), notify_challenges())


async def cancel_challenge(ws):
    logger.info("Cancelling challenge")

    if ws not in CHALLENGES:
        return await ws.send(challenge_error_event("Challenge not exists"))

    challenge = CHALLENGES.pop(ws)

    return await asyncio.gather(
        *[player.send(challenge_ok_event("cancelled")) for player in challenge.joined]
    )


async def join_challenge(ws, data):
    challenge_id = int(data['challenge_id'])
    player = PLAYERS[ws]

    challenge = CHALLENGES.get(challenge_id)
    if not challenge:
        return await ws.send(challenge_error_event(f"Challenge not found: {challenge_id}"))

    if player in challenge.blacklist:
        return await ws.send(challenge_error_event("Not allowed to join"))

    ready = challenge.join_player(player, challenge.data)

    return await asyncio.gather(
        *[
            player.send(challenge_join_event(challenge, player, data, ready))
            for player in challenge.joined
        ]
    )


def accept_challenge(ws, data):
    pass


def decline_challenge(ws, data):
    pass


def revise_challenge(ws, data):
    pass


async def handle_challenge(ws, data: dict):
    logger.info('handle_challenge')

    player = PLAYERS[ws]
    if not player.logged_in:
        raise AuthenticationError("Player not logged in")

    action = data.pop('action')
    if action == NEW_CHALLENGE:
        await create_challenge(ws, data)

    elif action == CANCEL_CHALLENGE:
        await cancel_challenge(ws)

    elif action == JOIN_CHALLENGE:
        await join_challenge(ws, data)

    else:
        raise InvalidMessageError(f"Invalid action: {action}")
