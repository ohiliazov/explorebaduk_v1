import asyncio

from explorebaduk.database import UserModel


class Challenge:
    def __init__(self, user: UserModel, data: dict = None):

        self.ws_list = set()
        self._user = user

        self.data = data
        self.joined = set()

        self._event = asyncio.Event()

    @property
    def user_id(self):
        return self._user.user_id

    def add_ws(self, ws):
        self.ws_list.add(ws)

    def remove_ws(self, ws):
        self.ws_list.discard(ws)

        if not self.ws_list:
            self._event.set()

    def as_dict(self):
        return {
            "player_id": self.user_id,
            "challenge": self.data,
            "joined": len(self.joined),
        }
