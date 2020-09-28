import asyncio

from websockets import WebSocketCommonProtocol
from explorebaduk.validation import challenge_validator


class Challenge:
    def __init__(self, ws: WebSocketCommonProtocol, user, data: dict = None):
        self.ws = ws
        self.user = user
        self.data = data
        self.joined = {}

        self.exit_event = asyncio.Event()

    @property
    def user_id(self):
        return self.user.user_id

    def join(self, user_id, ws):
        self.joined[user_id] = ws

    def leave(self, user_id):
        return self.joined.pop(user_id, None)

    def select(self, user_id):
        return self.joined.get(user_id)

    def is_active(self):
        return self.data and not self.ws.closed

    def set(self, data: dict):
        if challenge_validator.validate(data):
            self.data = challenge_validator.normalized(data)
        else:
            self.data = data  # TODO: remove after test

        self.exit_event.clear()
        return self.data

    def unset(self):
        self.exit_event.set()

        if data := self.data:
            self.data = None

        return data

    def as_dict(self):
        return {
            "user_id": self.user_id,
            "challenge": self.data,
            "joined": len(self.joined),
        }
