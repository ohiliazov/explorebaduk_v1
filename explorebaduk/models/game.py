import random

from explorebaduk.gameplay.kifu import Kifu
from explorebaduk.models.player import Player
from explorebaduk.models.challenge import Challenge
from explorebaduk.models.timer import create_timer


class GamePlayer:
    def __init__(self, player: Player, time_settings: dict):
        self.player = player
        self.timer = create_timer(**time_settings)

    @property
    def time_left(self):
        return self.timer.time_left

    def start_timer(self):
        self.timer.start()

    def stop_timer(self):
        self.timer.stop()


class Game:
    def __init__(self, game_id, black: Player, white: Player, challenge: Challenge):
        self.game_id = game_id
        self.black = GamePlayer(black, challenge.time_settings)
        self.white = GamePlayer(white, challenge.time_settings)
        self.kifu = Kifu(challenge.width, challenge.height)

    def __str__(self):
        return f"ID[{self.game_id}]B[{self.black.player}]W[{self.white.player}]"

    @property
    def whose_turn(self):
        return self.kifu.turn_color

    def play_move(self, color: str, coord: str):
        if color != self.whose_turn:
            raise Exception("Invalid player data")
        self.kifu.play_move(color, coord)

    def make_pass(self, color: str):
        if color != self.whose_turn:
            raise Exception("Invalid player data")
        self.kifu.make_pass(color)


if __name__ == "__main__":
    from explorebaduk.constants import TimeSystem

    black = Player(None, 1)
    white = Player(None, 2)

    black, white = random.sample([black, white], 2)
    black_timer = create_timer(TimeSystem.ABSOLUTE, main_time=3600)
    white_timer = create_timer(TimeSystem.ABSOLUTE, main_time=3600)

    black = GamePlayer(black, black_timer)
    white = GamePlayer(white, white_timer)

    game = Game(1, black, white, 19, 19)
