from itertools import repeat
from typing import List

from explorebaduk.gameplay.board import Location
from explorebaduk.gameplay.kifu import Kifu


class GamePlayer:
    def __init__(self, user, timer, color: Location):
        self.user = user
        self.timer = timer
        self.color = color

    def start_timer(self):
        self.timer.start()

    def stop_timer(self):
        self.timer.stop()


class Game:
    def __init__(self, players: List[GamePlayer], width: int, height: int, turn: str, handicap: int, komi: float):
        self._players = repeat(players)
        self._next_player = next(self._players)
        self.kifu = Kifu(width, height, handicap, komi, turn)
        self.handicap = handicap
        self.komi = komi

    @property
    def whose_turn(self) -> GamePlayer:
        return self._next_player

    @property
    def turn_color(self) -> Location:
        return self.whose_turn.color
