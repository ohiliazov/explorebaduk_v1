import asyncio
import logging
import json

from explorebaduk.constants import (
    NEW_CHALLENGE,
    CANCEL_CHALLENGE,
    JOIN_CHALLENGE,
    CHALLENGE, OK, ERROR
)
from explorebaduk.exceptions import AuthenticationError, InvalidMessageError
from explorebaduk.models import Challenge, Player
from explorebaduk.server import PLAYERS, CHALLENGES, get_by_user_id, notify_challenges
from explorebaduk.schema import NewChallengeSchema

logger = logging.getLogger('challenge_handler')


class ChallengeError(Exception):
    pass


def next_id_gen():
    next_id = 0

    while True:
        next_id += 1
        yield next_id


id_gen = next_id_gen()


def challenge_ok_event(message: str):
    return json.dumps({'type': CHALLENGE, 'result': OK, 'message': message})


def challenge_join_event(challenge: Challenge, player: Player, data: dict = None):
    return json.dumps({'type': CHALLENGE,
                       'action': JOIN_CHALLENGE,
                       'challenge_id': challenge.id,
                       'player': player.to_dict(),
                       'data': data})


def challenge_error_event(error_message: str):
    return json.dumps({'type': CHALLENGE, 'result': ERROR, 'message': error_message})


async def create_challenge(ws, data):
    if ws in CHALLENGES:
        return await ws.send(challenge_error_event('Challenge already exists'))

    data = NewChallengeSchema().load(data)
    player = PLAYERS[ws]

    challenge_id = next(id_gen)
    CHALLENGES[challenge_id] = Challenge(challenge_id, player, data)
    logger.info('Challenge created by: %s', PLAYERS[ws].user.full_name)
    return await asyncio.gather(ws.send(f"OK challenge new {next(id_gen)}"), notify_challenges())


async def cancel_challenge(ws):
    logger.info("Cancelling challenge")

    if ws not in CHALLENGES:
        return await ws.send(challenge_error_event('Challenge not exists'))

    challenge = CHALLENGES.pop(ws)

    return await asyncio.gather(*[player.send(challenge_ok_event('cancelled')) for player in challenge.joined])


async def join_challenge(ws, data):
    data = ChallengeJoinSchema().load(data)
    player = PLAYERS[ws]

    if not data['creator_id']:
        return await ws.send(challenge_error_event('Challenge ID is not provided'))

    creator_ws = get_by_user_id(data['creator_id'])

    if not creator_ws:
        return await ws.send(challenge_error_event('Player not found'))

    if creator_ws not in CHALLENGES:
        return await ws.send(challenge_error_event('Challenge not found'))

    challenge = CHALLENGES[creator_ws]

    if player in challenge.blacklist:
        return await ws.send(challenge_error_event('You are in blacklist'))

    challenge.join_player(player, data)

    return await asyncio.gather(*[player.send(challenge_join_event(challenge, player, data))
                                  for player in challenge.joined])


def accept_challenge(ws, data):
    pass


def decline_challenge(ws, data):
    pass


def revise_challenge(ws, data):
    pass


async def handle_challenge(ws, data: dict):
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
