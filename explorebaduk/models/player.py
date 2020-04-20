from enum import Enum

from explorebaduk.database import UserModel


class PlayerStatus(Enum):
    IDLE = "idle"
    PLAYING = "playing"
    OBSERVING = "observing"


class Player:
    def __init__(self, ws, user: UserModel):
        self.ws = ws
        self.user = user
        self.status = PlayerStatus.IDLE

    async def send(self, message: str):
        return await self.ws.send(message)

    @property
    def id(self):
        return self.user.user_id

    @property
    def full_name(self):
        return self.user.full_name

    @property
    def rating(self):
        return self.user.rating

    def __str__(self):
        return f"ID[{self.id}]NM[{self.full_name}]RT[{self.rating}]"
