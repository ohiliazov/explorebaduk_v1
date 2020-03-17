from typing import Set

from explorebaduk.models.player import Player


class Challenge:
    def __init__(self, player: Player, data: dict):
        self.challenge_id = player.id
        self.creator = player

        # game info
        self.name = data["name"]
        self.width = data["width"]
        self.height = data["height"]

        # # flags
        # self.is_open = data["is_open"]
        # self.undo = data["undo"]
        # self.pause = data["pause"]

        # time control
        self.time_system = data["time_system"]
        self.main_time = data["main_time"]
        self.overtime = data["overtime"]
        self.periods = data["periods"]
        self.stones = data["stones"]
        self.bonus = data["bonus"]

        self.pending: Set[Player] = set()

    def __str__(self):
        return (
            f"ID[{self.challenge_id}]GN[{self.name}]SZ[{self.width}:{self.height}]"
            # f"FL[{self.is_open:d}{self.undo:d}{self.pause:d}]"
            f"TS[{self.time_system.value}M{self.main_time}O{self.overtime}P{self.periods}S{self.stones}B{self.bonus}]"
        )

    @property
    def time_settings(self):
        return {
            "time_system": self.time_system,
            "main_time": self.main_time,
            "overtime": self.overtime,
            "periods": self.periods,
            "stones": self.stones,
            "bonus": self.bonus,
        }

    async def add_player(self, player: Player):
        self.pending.add(player)

    async def remove_player(self, player: Player):
        self.pending.remove(player)
