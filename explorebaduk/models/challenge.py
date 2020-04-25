from typing import Set

from explorebaduk.models.player import Player
from explorebaduk.models.game import Game


class Challenge:
    def __init__(self, challenge_id: int, creator: Player, game: Game):
        self.challenge_id = challenge_id
        self.creator = creator
        self.game = game
        self.pending: Set[Player] = set()

    def __str__(self):
        return f"ID[{self.challenge_id}]{self.game}{self.game.time_control}"

    async def add_player(self, player: Player):
        self.pending.add(player)

    async def remove_player(self, player: Player):
        self.pending.remove(player)
