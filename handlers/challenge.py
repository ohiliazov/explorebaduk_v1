import logging

from constants import (
    CHALLENGE_CREATE,
    CHALLENGE_ACCEPT,
    CHALLENGE_DECLINE,
    CHALLENGE_REVISE
)
from handlers import BaseHandler, InvalidActionError

logger = logging.getLogger('challenge_handler')


class ChallengeHandler(BaseHandler):
    PRIORITY = 3

    def __init__(self, session, sync_queue):
        super().__init__(session, sync_queue)
        self.challenges = {}

    def create_challenge(self, ws, data):
        pass

    def accept_challenge(self, ws, data):
        pass

    def decline_challenge(self, ws, data):
        pass

    def revise_challenge(self, ws, data):
        pass

    def handle_action(self, ws, action: str, data: dict):
        if action == CHALLENGE_CREATE:
            self.create_challenge(ws, data)

        elif action == CHALLENGE_ACCEPT:
            self.accept_challenge(ws, data)

        elif action == CHALLENGE_DECLINE:
            self.decline_challenge(ws, data)

        elif action == CHALLENGE_REVISE:
            self.revise_challenge(ws, data)

        else:
            raise InvalidActionError(f"Invalid action: {action}")
