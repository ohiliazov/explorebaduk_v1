import random

from explorebaduk.database import TimerModel, db
from explorebaduk.gameplay.kifu import Kifu
from explorebaduk.models.player import Player
from explorebaduk.models.challenge import Challenge
from explorebaduk.models.timer import Timer


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
