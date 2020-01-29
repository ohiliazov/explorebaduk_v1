import itertools
import logging
from typing import List, Tuple

from explorebaduk.exceptions import GameError
from explorebaduk.gameplay.board import Location
from explorebaduk.gameplay.kifu import Kifu

logger = logging.getLogger("game")


class GamePlayer:
    def __init__(self, user, timer, color: Location):
        self.user = user
        self.timer = timer
        self.color = color

    def start_timer(self):
        return self.timer.start()

    def stop_timer(self):
        return self.timer.stop()


class Game:
    def __init__(
        self, players: List[GamePlayer], info: dict, width: int, height: int, turn: str, handicap: int, komi: float
    ):
        self._players_queue = itertools.cycle(players)
        self._next_player = None
        self.kifu = Kifu(width, height, handicap, komi, turn)

        self.info = info

    @property
    def whose_turn(self) -> GamePlayer:
        if self._next_player is None:
            raise GameError("Not started")
        return self._next_player

    def start_game(self) -> Tuple[GamePlayer, float]:
        logger.info("start_game")
        self._next_player = next(self._players_queue)
        time_left = self.whose_turn.start_timer()

        return self.whose_turn, time_left

    def play_move(self, user):
        pass
