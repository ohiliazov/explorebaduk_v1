import logging

from explorebaduk.constants import (
    CHALLENGE_CREATE,
    CHALLENGE_CANCEL,
    CHALLENGE_ACCEPT,
    CHALLENGE_DECLINE,
    CHALLENGE_REVISE,
)
from explorebaduk.server import eb_server
from explorebaduk.schema import ChallengeSchema

logger = logging.getLogger('challenge_handler')


class Challenge:
    def __init__(self, ws, data):
        self.creator = ws
        self.data = data
        self.status = 'open'
        self.joined = {}

    def join(self, ws, data):
        print("New player joined")
        self.joined[ws] = data

    def accept(self, ws, data):
        print("Start game")


class ChallengeError(Exception):
    pass


def create_challenge(ws, data):
    data = ChallengeSchema().load(data)
    eb_server[ws] = data


def cancel_challenge(ws):
    logger.info("Cancelling challenge")
    eb_server.pop(ws, None)


def join_challenge(ws, data):
    pass


def accept_challenge(ws, data):
    pass


def decline_challenge(ws, data):
    pass


def revise_challenge(ws, data):
    pass


def handle_challenge(ws, action: str, data: dict):
    if not eb_server.get(ws):
        raise ChallengeError("Not logged in")

    if action == CHALLENGE_CREATE:
        create_challenge(ws, data)

    elif action == CHALLENGE_CANCEL:
        accept_challenge(ws, data)

    elif action == CHALLENGE_ACCEPT:
        accept_challenge(ws, data)

    elif action == CHALLENGE_DECLINE:
        decline_challenge(ws, data)

    elif action == CHALLENGE_REVISE:
        revise_challenge(ws, data)
