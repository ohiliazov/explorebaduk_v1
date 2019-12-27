from typing import Set

from explorebaduk.models.player import Player


class Game:
    def __init__(self, players: Set[Player] = None):
        self.players: Set[Player] = players or set()
        self.joined: Set[Player] = set()

    @property
    def players_joined(self):
        return all([player in self.joined for player in self.players])
