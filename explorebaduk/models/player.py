import asyncio
from typing import Optional
from websockets import WebSocketCommonProtocol

from explorebaduk.database import PlayerModel


class Player:
    def __init__(self, ws: WebSocketCommonProtocol, player: Optional[PlayerModel]):
        self.ws = ws
        self.player = player

        self.exit_event = asyncio.Event()

    def as_dict(self):
        if self.player:
            return {
                "player_id": self.player.user_id,
                "username": self.player.username,
                "first_name": self.player.first_name,
                "last_name": self.player.last_name,
                "email": self.player.email,
                "rating": round(self.player.rating, 2),
                "puzzle_rating": round(self.player.puzzle_rating, 2),
            }

    @property
    def authorized(self) -> bool:
        return self.player is not None
