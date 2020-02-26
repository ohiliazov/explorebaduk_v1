import random

from explorebaduk.gameplay.board import Location
from explorebaduk.gameplay.kifu import Kifu
from explorebaduk.models.player import Player
from explorebaduk.models.challenge import Challenge
from explorebaduk.models.timer import create_timer


class GamePlayer:
    def __init__(self, player: Player, color: Location, timer):
        self.player = player
        self.timer = timer
        self.color = color

    def start_timer(self):
        self.timer.start()

    def stop_timer(self):
        self.timer.stop()


class Game:
    def __init__(self, game_id, black: GamePlayer, white: GamePlayer, width: int, height: int):
        self.game_id = game_id
        self.black = black
        self.white = white
        self._next_player = self.black
        self.kifu = Kifu(width, height)

    def __str__(self):
        return f"ID[{self.game_id}]B[{self.black.player}]W[{self.white.player}]"

    @property
    def whose_turn(self) -> GamePlayer:
        return self._next_player

    @property
    def turn_color(self) -> Location:
        return self.whose_turn.color

    @classmethod
    def from_challenge(cls, game_id, challenge: "Challenge", against: Player):
        black, white = random.sample([challenge.creator, against], 2)

        black_timer = create_timer(challenge.time_system, **challenge.time_control)
        white_timer = create_timer(challenge.time_system, **challenge.time_control)

        black = GamePlayer(black, Location.BLACK, black_timer)
        white = GamePlayer(white, Location.WHITE, white_timer)

        return cls(game_id, black, white, challenge.width, challenge.height)

    def play_move(self, color, coords):
        pass
