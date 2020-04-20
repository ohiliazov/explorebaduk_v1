from typing import Set

from explorebaduk.models.player import Player
from explorebaduk.models.timer import TimeControl


class Challenge:
    def __init__(self, player: Player, data: dict):
        self.challenge_id = player.id
        self.creator = player

        # game info
        self.name = data["name"]
        self.width = data["width"]
        self.height = data["height"]

        # time control
        self.time_control = TimeControl(**data)

        self.pending: Set[Player] = set()

    def __str__(self):
        return f"ID[{self.challenge_id}]GN[{self.name}]SZ[{self.width}:{self.height}]{self.time_control}"

    async def add_player(self, player: Player):
        self.pending.add(player)

    async def remove_player(self, player: Player):
        self.pending.remove(player)
