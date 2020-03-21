import random

from explorebaduk.database.timer import TimerModel
from explorebaduk.gameplay.kifu import Kifu
from explorebaduk.models.player import Player
from explorebaduk.models.challenge import Challenge
from explorebaduk.models.timer import create_timer
from explorebaduk.handlers.database import db


class GameTimer:
    def __init__(self, game_id: int, player: Player, time_settings: dict):
        self._db_timer = None
        self.game_id = game_id
        self.player = player
        self.time_settings = time_settings
        self.timer = create_timer(**time_settings)

    @property
    def db_timer(self) -> TimerModel:
        if self._db_timer is None:
            self._db_timer = TimerModel(
                game_id=self.game_id,
                player_id=self.player.id,
                time_system=self.time_settings["time_system"].value,
                main_time=self.time_settings["main_time"],
                overtime=self.time_settings["overtime"],
                periods=self.time_settings["periods"],
                stones=self.time_settings["stones"],
                bonus=self.time_settings["bonus"],
                time_left=self.time_left
            )

            db.add(self._db_timer)
            db.commit()

        return self._db_timer

    @property
    def time_left(self):
        return self.timer.time_left

    def save_to_db(self):
        self.db_timer.time_left = self.time_left
        db.add(self.db_timer)
        db.commit()

    def start_timer(self):
        self.timer.start()

    def stop_timer(self):
        self.timer.stop()
        self.save_to_db()


class Game:
    def __init__(self, game_id, black: Player, white: Player, challenge: Challenge):
        self.game_id = game_id

        self.name = challenge.name
        self.width = challenge.width
        self.height = challenge.height
        self.time_settings = challenge.time_settings

        self.black = GameTimer(game_id, black, self.time_settings)
        self.white = GameTimer(game_id, white, self.time_settings)

        self.kifu = Kifu(self.width, self.height)

    def __str__(self):
        return f"ID[{self.game_id}]B[{self.black.player}]W[{self.white.player}]"

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
