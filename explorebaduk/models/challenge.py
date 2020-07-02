from typing import Set

from explorebaduk.models.user import User
from explorebaduk.models.timer import TimeControl


class ChallengeInfo:
    def __init__(self, name: str, width: int, height: int, rules: str):
        self.name = name
        self.width = width
        self.height = height
        self.rules = rules

    def __str__(self):
        return f"GN[{self.name}]SZ[{self.width}:{self.height}]RU[{self.rules}]"


class Challenge:
    def __init__(self, creator: User, data: dict):
        self.creator = creator
        self.info = ChallengeInfo(**data)
        self.time_control = TimeControl(**data)
        self.pending: Set[User] = set()

    def __str__(self):
        return f"ID[{self.creator.id}]{self.info}{self.time_control}"

    async def join_player(self, player: User):
        self.pending.add(player)

    async def leave_player(self, player: User):
        self.pending.remove(player)
