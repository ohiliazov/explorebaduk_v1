import asyncio

from explorebaduk.database import UserModel


class Player:
    def __init__(self, user: UserModel = None):
        self.ws_list = set()
        self._user = user

        self._event = asyncio.Event()

    @property
    def user_id(self):
        return self._user.user_id

    @property
    def online(self):
        return bool(self.ws_list)

    @property
    def authorized(self):
        return self._user is not None

    async def wait_offline(self):
        await self._event.wait()

    def add_ws(self, ws):
        self.ws_list.add(ws)

    def remove_ws(self, ws):
        self.ws_list.discard(ws)

        if not self.ws_list:
            self._event.set()

    def as_dict(self):
        if self._user:
            return self._user.as_dict()
