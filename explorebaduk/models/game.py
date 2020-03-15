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
    def turn_color(self):
        return self.kifu.turn_color

    @property
    def current_player(self):
        return self.black if self.turn_color == "black" else self.white

    @property
    def history(self):
        return self.kifu.history

    @property
    def finished(self):
        return (self.history[-1] == 'pass' and self.history[-2] == 'pass') if len(self.history) > 1 else False

    def get_player(self, color: str):
        if color == "black":
            return self.black
        elif color == "white":
            return self.white

    def play_move(self, color: str, coord: str):
        if self.finished:
            raise Exception("Game finished")
        if color != self.turn_color:
            raise Exception("Invalid player data")
        self.kifu.play_move(color, coord)

    def make_pass(self, color: str):
        if color != self.turn_color:
            raise Exception("Invalid player data")

        player = self.get_player(color)
        player.stop_timer()
        self.kifu.make_pass(color)
        opponent = []

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
