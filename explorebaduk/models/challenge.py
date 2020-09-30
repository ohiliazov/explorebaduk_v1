import asyncio

from explorebaduk.models.player import Player


class Challenge:
    def __init__(self, player: Player, data: dict = None):
        self.player = player
        self.data = data
        self.joined = {}

        self.exit_event = asyncio.Event()

    def is_active(self):
        return self.data and self.player.ws_list

    def as_dict(self):
        return {
            "player_id": self.player.user.user_id,
            "challenge": self.data,
            "joined": len(self.joined),
        }
