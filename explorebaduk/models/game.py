import random

from explorebaduk.gameplay.kifu import Kifu
from explorebaduk.models.player import Player
from explorebaduk.models.challenge import Challenge
from explorebaduk.models.timer import Timer, create_timer


class GamePlayer:
    def __init__(self, player: Player, timer: Timer):
        self.player = player
        self.timer = timer

    @property
    def time_left(self):
        return self.timer.time_left

    def start_timer(self):
        self.timer.start()

    def stop_timer(self):
        self.timer.stop()


class Game:
    def __init__(self, game_id, black: GamePlayer, white: GamePlayer, width: int, height: int):
        self.game_id = game_id
        self.black = black
        self.white = white
        self.players = {
            "black": black,
            "white": white,
        }
        self.kifu = Kifu(width, height)

    def __str__(self):
        return f"ID[{self.game_id}]B[{self.black.player}]W[{self.white.player}]"

    @classmethod
    def from_challenge(cls, game_id, challenge: "Challenge", against: Player):
        black, white = random.sample([challenge.creator, against], 2)

        black_timer = create_timer(challenge.time_system, **challenge.time_control)
        white_timer = create_timer(challenge.time_system, **challenge.time_control)

        black = GamePlayer(black, black_timer)
        white = GamePlayer(white, white_timer)

        return cls(game_id, black, white, challenge.width, challenge.height)

    def play_move(self, player: Player, color: str, coord: str):
        if self.players[color].player is not player:
            raise Exception("Invalid player data")
        self.kifu.play_move(color, coord)

    def make_pass(self, player: Player, color: str):
        if self.players[color].player is not player:
            raise Exception("Invalid player data")
        self.kifu.make_pass(color)


if __name__ == '__main__':
    from explorebaduk.constants import TimeSystem
    black = Player(None, 1)
    white = Player(None, 2)

    black, white = random.sample([black, white], 2)
    black_timer = create_timer(TimeSystem.ABSOLUTE, main_time=3600)
    white_timer = create_timer(TimeSystem.ABSOLUTE, main_time=3600)

    black = GamePlayer(black, black_timer)
    white = GamePlayer(white, white_timer)

    game = Game(1, black, white, 19, 19)
