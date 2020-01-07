import json
from enum import Enum

from typing import Optional

from explorebaduk.database import UserModel


class PlayerStatus(Enum):
    IDLE = 'idle'
    PLAYING = 'playing'


class Player:
    def __init__(self, ws):
        self.ws = ws
        self._user: Optional[UserModel] = None
        self.status = PlayerStatus.IDLE

    async def send(self, data: str):
        return self.ws.send(json.dumps(data))

    def __str__(self):
        if self.logged_in:
            return f"{self.full_name} [{self.rating}]"

    @property
    def user(self):
        return self._user

    @property
    def logged_in(self):
        return self.user is not None

    @property
    def id(self):
        if self.logged_in:
            return self.user.user_id

    @property
    def full_name(self):
        if self.logged_in:
            return self.user.full_name

    @property
    def rating(self):
        if self.logged_in:
            return self.user.rating

    def to_dict(self) -> dict:
        if self.logged_in:
            return {
                'user_id': self.id,
                'full_name': self.full_name,
                'rating': self.rating,
            }

    def login(self, user: UserModel):
        self._user = user

    def logout(self):
        self._user = None
