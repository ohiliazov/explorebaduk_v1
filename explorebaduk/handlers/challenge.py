import logging

from explorebaduk.constants import (
    CHALLENGE_CREATE,
    CHALLENGE_ACCEPT,
    CHALLENGE_DECLINE,
    CHALLENGE_REVISE
)
from explorebaduk.server import eb_server

logger = logging.getLogger('challenge_handler')


def create_challenge(ws, data):
    pass


def accept_challenge(ws, data):
    pass


def decline_challenge(ws, data):
    pass


def revise_challenge(ws, data):
    pass


def handle_challenge(ws, action: str, data: dict):
    if action == CHALLENGE_CREATE:
        create_challenge(ws, data)

    elif action == CHALLENGE_ACCEPT:
        accept_challenge(ws, data)

    elif action == CHALLENGE_DECLINE:
        decline_challenge(ws, data)

    elif action == CHALLENGE_REVISE:
        revise_challenge(ws, data)
