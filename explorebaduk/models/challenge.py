from typing import Dict

from explorebaduk.models.player import Player

JOINED = "joined"
ACCEPTED = "accepted"


class Challenge:
    def __init__(self, challenge_id: int, creator: Player, data: dict):

        self.id = challenge_id
        self.creator = creator
        self.blacklist = set()

        self.name = data.pop("name")
        self.game_type = data.pop("game_type")
        self.rules = data.pop("rules")
        self.players_num = data.pop("players_num")
        self.data = data

        self.joined: Dict[Player, Dict[str, str]] = {self.creator: {"status": ACCEPTED}}

    @property
    def board_size(self):
        return f"{self.data['width']}:{self.data['height']}"

    def __str__(self):
        return (
            f"{self.id} {self.name} "
            f"GT{self.game_type.value}RL{self.rules.value}PL{self.players_num} {self.board_size} "
            f"F{int(self.data['is_open'])}{int(self.data['undo'])}{int(self.data['pause'])} "
            f"T{self.data['time_system'].value}M{self.data['main_time']}"
            f"O{self.data['overtime']}P{self.data['periods']}S{self.data['stones']}"
            f"B{self.data['bonus']}D{self.data['delay']}"
        )

    @property
    def status(self):
        return {player.id: data["status"] for player, data in self.joined.items()}

    @property
    def ready(self):
        return list(self.status.values()).count(ACCEPTED) == 2

    def join_player(self, player: Player, data: dict):
        self.joined[player] = {
            "status": JOINED,
            "data": data,
        }

        return self.ready

    def accept_player(self, player: Player):
        self.joined[player]["status"] = ACCEPTED

    def remove_player(self, player: Player):
        self.joined.pop(player)

    def return_player(self, player):
        raise NotImplementedError

    def accept_edits(self, player):
        raise NotImplementedError

    def revise_edits(self, player):
        raise NotImplementedError

    def add_to_blacklist(self, player):
        raise NotImplementedError

    def to_dict(self):
        return {
            "data": self.data,
            "status": self.status,
        }
