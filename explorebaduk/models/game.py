import datetime
import random

from explorebaduk.database import GameModel, GamePlayerModel
from explorebaduk.gameplay.kifu import Kifu
from explorebaduk.mixins import DatabaseMixin
from explorebaduk.models.player import Player
from explorebaduk.models.challenge import Challenge
from explorebaduk.models.timer import Timer


class GamePlayer(DatabaseMixin):
    db_model = GamePlayerModel
    columns = [
        "game_id",
        "player_id",
        "time_left",
    ]

    def __init__(self, game_id: int, player_id: int, timer: Timer):
        self.game_id = game_id
        self.player_id = player_id
        self.timer = timer

    @property
    def time_left(self):
        return self.timer.time_left


class Game(DatabaseMixin):
    db_model = GameModel
    columns = [
        "name",
        "width",
        "height",
        "time_system",
        "main_time",
        "overtime",
        "periods",
        "stones",
        "bonus",
        "started_at",
        "sgf",
    ]

    def __init__(self, challenge: Challenge):
        self.name = challenge.name
        self.width = challenge.width
        self.height = challenge.height
        self.time_system = challenge.time_system
        self.main_time = challenge.main_time
        self.overtime = challenge.overtime
        self.periods = challenge.periods
        self.stones = challenge.stones
        self.bonus = challenge.bonus
        self.started_at = datetime.datetime.utcnow()

        self.kifu = Kifu(self.width, self.height)
        self.create_model()

    @property
    def sgf(self):
        return str(self.kifu.cursor.game)


class GameManager:
    def __init__(self, game: Game, black: GamePlayer, white: GamePlayer):
        self.game = game
        self.black = black
        self.white = white


class Game:
    def __init__(self, game_id, black: Player, white: Player, black_timer: Timer, white_timer: Timer,
                 challenge: Challenge):
        self.game_id = game_id

        self.name = challenge.name
        self.width = challenge.width
        self.height = challenge.height
        self.time_settings = challenge.time_settings

        self.black = black
        self.black_timer = black_timer
        self.white = white
        self.white_timer = white_timer
        self.kifu = Kifu(self.width, self.height)

    def __str__(self):
        return f"ID[{self.game_id}]B[{self.black.id}]W[{self.white.id}]"

    def save_to_db(self):
        pass

    @property
    def turn_color(self):
        return self.kifu.turn_color

    @property
    def current(self):
        return self.black if self.turn_color == "black" else self.white

    @property
    def history(self):
        return self.kifu.history

    @property
    def finished(self):
        return (self.history[-1] == "pass" and self.history[-2] == "pass") if len(self.history) > 1 else False

    def get_player(self, color: str):
        if color == "black":
            return self.black
        elif color == "white":
            return self.white

    def _flip_timers(self):
        if self.black.timer.started:
            self.black.stop_timer()
            self.white.start_timer()
        else:
            self.white.stop_timer()
            self.black.start_timer()

    def play_move(self, coord: str):
        if coord == "pass":
            position = self.kifu.make_pass()
        else:
            position = self.kifu.play_move(coord)

        print(position)
        self._flip_timers()

        return position


if __name__ == "__main__":
    from explorebaduk.constants import TimeSystem

    black = Player(None, 1)
    white = Player(None, 2)

    black, white = random.sample([black, white], 2)
    black_timer = create_timer(TimeSystem.ABSOLUTE, main_time=3600)
    white_timer = create_timer(TimeSystem.ABSOLUTE, main_time=3600)

    black = GameTimer(black, black_timer)
    white = GameTimer(white, white_timer)

    game = Game(1, black, white, 19, 19)
