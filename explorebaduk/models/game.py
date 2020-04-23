import datetime

from sgftree.sgf import SGF

from explorebaduk.database import db
from explorebaduk.mixins import DatabaseMixin
from explorebaduk.models.player import Player
from explorebaduk.models.challenge import Challenge
from explorebaduk.models.timer import TimeControl


class GamePlayer(DatabaseMixin):
    def __init__(self, player: Player, time_control: TimeControl):
        self.player = player
        self.time_system = time_control.time_system
        self.main_time = time_control.main_time
        self.overtime = time_control.overtime
        self.periods = time_control.periods
        self.stones = time_control.stones
        self.bonus = time_control.bonus
        self.timer = time_control.timer()

    @property
    def time_left(self):
        return self.timer.time_left

    def start_timer(self):
        return self.timer.start()

    def stop_timer(self):
        return self.timer.stop()


class Game:
    def __init__(self, challenge: Challenge, black: GamePlayer, white: GamePlayer):
        self.game_id = None
        self.name = challenge.name
        self.width = challenge.width
        self.height = challenge.height
        self.started_at = datetime.datetime.utcnow()

        self.sgf = SGF(self.width, self.height)

        self.black = black
        self.white = white

    @property
    def turn(self):
        return self.sgf.turn

    def __str__(self):
        return f"ID[{self.game_id}]GN[{self.name}]SZ[{self.width}:{self.height}]" \
               f"B[{self.black.player.id}]W[{self.white.player.id}]"

    def whose_turn(self):
        return self.black.player if self.turn == "black" else self.white.player
