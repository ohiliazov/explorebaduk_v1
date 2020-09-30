import asyncio
from typing import Optional

from explorebaduk.database import UserModel


class Player:
    def __init__(self, user: Optional[UserModel]):
        self.ws_list = set()
        self.user = user

        self.online_event = asyncio.Event()
        self.offline_event = asyncio.Event()

    @property
    def player_id(self):
        return self.user.user_id

    async def add_ws(self, ws):
        self.ws_list.add(ws)

        if len(self.ws_list) == 1:
            self.online_event.set()

    async def remove_ws(self, ws):
        self.ws_list.discard(ws)

        if not self.ws_list:
            self.offline_event.set()

    def as_dict(self):
        if self.user:
            return self.user.as_dict()
