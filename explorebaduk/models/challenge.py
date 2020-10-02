import asyncio

from explorebaduk.database import UserModel


class ChallengeStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"


class Challenge:
    def __init__(self, user: UserModel = None):

        self.ws_list = set()
        self._user = user

        self.data = None
        self.joined = set()

        self._event = asyncio.Event()

    @property
    def user_id(self):
        return self._user.user_id

    @property
    def authorized(self):
        return self._user is not None

    async def wait_offline(self):
        await self._event.wait()

    def is_active(self):
        return bool(self.data)

    def add_ws(self, ws):
        self.ws_list.add(ws)

    def remove_ws(self, ws):
        self.ws_list.discard(ws)

        if not self.ws_list:
            self._event.set()

    def as_dict(self):
        return self.data

    def set(self, data: dict):
        self.data = data

    def unset(self):
        self.data = None
