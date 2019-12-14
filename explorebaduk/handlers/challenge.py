import logging

from explorebaduk.constants import (
    CREATE_CHALLENGE,
    CANCEL_CHALLENGE,
)
from explorebaduk.exceptions import AuthenticationError, InvalidMessageError
from explorebaduk.models import Challenge
from explorebaduk.server import GameServer
from explorebaduk.schema import ChallengeSchema

logger = logging.getLogger('challenge_handler')


class ChallengeError(Exception):
    pass


async def create_challenge(ws, data):
    data = ChallengeSchema().load(data)
    player = GameServer.players[ws]
    GameServer.challenges[ws] = Challenge(player, data)
    logger.info('Challenge created by: %s', GameServer.players[ws].user.full_name)
    await GameServer.notify_challenges()


def cancel_challenge(ws):
    logger.info("Cancelling challenge")
    GameServer.challenges.pop(ws, None)


def join_challenge(ws, data):
    pass


def accept_challenge(ws, data):
    pass


def decline_challenge(ws, data):
    pass


def revise_challenge(ws, data):
    pass


async def handle_challenge(ws, action: str, data: dict):
    if not GameServer.players[ws].logged_in:
        raise AuthenticationError("Player not logged in")

    if action == CREATE_CHALLENGE:
        await create_challenge(ws, data)

    elif action == CANCEL_CHALLENGE:
        accept_challenge(ws, data)

    else:
        raise InvalidMessageError(f"Invalid action: {action}")
