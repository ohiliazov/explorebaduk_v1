from typing import Set

from explorebaduk.models.user import User


class Game:
    def __init__(self, players: Set[User] = None):
        self.players: Set[User] = players or set()
        self.joined: Set[User] = set()

    @property
    def players_joined(self):
        return all([player in self.joined for player in self.players])
