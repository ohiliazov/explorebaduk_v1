import json
from enum import Enum

from explorebaduk.database import UserModel


class PlayerStatus(Enum):
    IDLE = "idle"
    PLAYING = "playing"


class Player:
    def __init__(self, ws, user: UserModel):
        self.ws = ws
        self.user = user
        self.status = PlayerStatus.IDLE

    async def send(self, data: str):
        return self.ws.send(json.dumps(data))

    def __str__(self):
        if self.logged_in:
            return f"{self.id} {self.rating} {self.full_name}"

    @property
    def logged_in(self):
        return self.user is not None

    @property
    def id(self):
        return self.user.user_id

    @property
    def full_name(self):
        return self.user.full_name

    @property
    def rating(self):
        return self.user.rating

    @property
    def data(self):
        return self.id, self.full_name, self.rating
