import asyncio
from cerberus import Validator
from explorebaduk.database import UserModel
from explorebaduk.validation import challenge_schema


class ChallengeStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"


class Challenge:
    def __init__(self, user: UserModel = None):

        self.ws_list = set()
        self._user = user

        self.lock = asyncio.Lock()
        self.data = None
        self.joined = set()

    @property
    def user_id(self):
        return self._user.user_id

    @property
    def authorized(self):
        return self._user is not None

    @property
    def user_data(self):
        if self._user:
            return self._user.as_dict()

    def is_active(self):
        return bool(self.data)

    def add_ws(self, ws):
        self.ws_list.add(ws)

    def remove_ws(self, ws):
        self.ws_list.remove(ws)

    def as_dict(self):
        return self.data

    def set(self, data: dict):
        v = Validator(challenge_schema)
        self.data = v.validated(data)

        return v.errors

    def unset(self):
        data = self.data
        self.data = None
        return data
