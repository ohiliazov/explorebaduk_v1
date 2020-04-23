import asyncio
import datetime

from sgftree.sgf import SGF

from explorebaduk.database import db
from explorebaduk.mixins import DatabaseMixin
from explorebaduk.models.player import Player
from explorebaduk.models.challenge import Challenge
from explorebaduk.models.timer import TimeControl


class GameStatus:
    LOADING = "loading"
    PLAYING = "playing"
    SCORING = "scoring"
    FINISHED = "finished"


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

        self.state = GameStatus.LOADING

    @property
    def turn(self):
        return self.sgf.turn

    def __str__(self):
        return f"ID[{self.game_id}]GN[{self.name}]SZ[{self.width}:{self.height}]" \
               f"B[{self.black.player.id}]W[{self.white.player.id}]"

    @property
    def whose_turn(self):
        return self.black if self.turn == "black" else self.white

    def start_game(self) -> float:
        self.started_at = datetime.datetime.utcnow()
        self.state = GameStatus.PLAYING

        self.game_id = db.insert_game(self.name, self.width, self.height, self.started_at, str(self.sgf))
        return self.whose_turn.start_timer()

    async def sync_timers(self):
        message = f"game ID[{self.game_id}]PL[{self.turn}]BL[{self.black.time_left}]WL[{self.white.time_left}]"
        await asyncio.gather(
            self.black.player.send(message),
            self.white.player.send(message),
        )

    def make_move(self, coord):
        player_time_left = self.whose_turn.stop_timer()
        self.sgf.make_move(coord, player_time_left)
        opponent_time_left = self.whose_turn.start_timer()
        return player_time_left, opponent_time_left
