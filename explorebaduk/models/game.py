import datetime

from explorebaduk.database import db
from explorebaduk.gameplay.kifu import Kifu
from explorebaduk.mixins import DatabaseMixin
from explorebaduk.models.challenge import Challenge
from explorebaduk.models.timer import TimeControl


class Game:
    def __init__(self, challenge: Challenge):
        self.name = challenge.name
        self.width = challenge.width
        self.height = challenge.height
        self.started_at = datetime.datetime.utcnow()

        self.kifu = Kifu(self.width, self.height)
        self.model = db.insert_game(self.name, self.width, self.height)

    @property
    def sgf(self):
        return str(self.kifu.cursor.game)

    @property
    def game_id(self):
        return self.model.game_id


class GamePlayer(DatabaseMixin):
    def __init__(self, game_id: int, player_id: int, time_control: TimeControl):
        self.game_id = game_id
        self.player_id = player_id
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


class GameManager:
    def __init__(self, game: Game, black: GamePlayer, white: GamePlayer):
        self.game = game
        self.black = black
        self.white = white
