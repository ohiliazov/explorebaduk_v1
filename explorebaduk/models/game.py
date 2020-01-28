from typing import List

from explorebaduk.models.user import User
from explorebaduk.models.challenge import Challenge


class Game:
    def __init__(self, black_players: List[User], white_players: List[User], time_settings: dict):
        self.black_players = black_players
        self.white_players = white_players

    @classmethod
    def from_challenge(cls, challenge: Challenge):
        pass
