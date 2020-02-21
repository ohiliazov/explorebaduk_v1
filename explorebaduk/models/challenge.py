import asyncio

from typing import Dict

from explorebaduk.models.player import Player
from explorebaduk.constants import PlayerColor


class PlayerRequest:
    def __init__(self, player: Player, data: dict):
        self.player: Player = player
        self.color: PlayerColor = data["color"]
        self.handicap: int = data["handicap"]
        self.komi: float = data["komi"]

    def __str__(self):
        return f"{self.player}CL[{self.color.value}]HN[{self.handicap}]KM[{self.komi}]"


class Challenge:
    def __init__(self, challenge_id, creator: Player, data: dict):
        self.challenge_id = challenge_id
        self.creator = creator

        self.name = data["name"]

        # game info
        self.game_type = data["game_type"].value
        self.rules = data["rules"].value
        self.width = data["width"]
        self.height = data["height"]
        self.rank_lower = data["rank_lower"]
        self.rank_upper = data["rank_upper"]

        # flags
        self.is_open = data["is_open"]
        self.undo = data["undo"]
        self.pause = data["pause"]

        # time control
        self.time_system = data["time_system"].value
        self.main_time = data["main_time"]
        self.overtime = data["overtime"]
        self.periods = data["periods"]
        self.stones = data["stones"]
        self.bonus = data["bonus"]
        self.delay = data["delay"]

        self.pending: Dict[Player, PlayerRequest] = {}

    def __str__(self):
        return (
            f"ID[{self.challenge_id}]GN[{self.name}]"
            f"GI[{self.game_type}R{self.rules}W{self.width}H{self.height}MIN{self.rank_lower}MAX{self.rank_upper}]"
            f"FL[{self.is_open:d}{self.undo:d}{self.pause:d}]"
            f"TS[{self.time_system}M{self.main_time}"
            f"O{self.overtime}P{self.periods}S{self.stones}B{self.bonus}D{self.delay}]"
        )

    async def notify_creator(self, message):
        await self.creator.send(message)

    def join_player(self, player: Player, data: dict):
        player_request = PlayerRequest(player, data)
        self.pending[player] = player_request

        return player_request

    def leave_player(self, player: Player):
        return self.pending.pop(player)
