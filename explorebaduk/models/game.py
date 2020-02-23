import random

from explorebaduk.gameplay.board import Location
from explorebaduk.gameplay.kifu import Kifu
from explorebaduk.models.player import Player
from explorebaduk.models.challenge import Challenge
from explorebaduk.models.timer import create_timers


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
    def __init__(self, black: GamePlayer, white: GamePlayer, width: int, height: int):
        self.black = black
        self.white = white
        self._next_player = self.black
        self.kifu = Kifu(width, height)

    @property
    def whose_turn(self) -> GamePlayer:
        return self._next_player

    @property
    def turn_color(self) -> Location:
        return self.whose_turn.color

    @classmethod
    def from_challenge(cls, challenge: "Challenge", against: Player):
        black, white = random.sample([challenge.creator, against])
        black_timer, white_timer = create_timers(challenge.time_system, 2, **challenge.time_control)
        black = GamePlayer(black, Location.BLACK, black_timer)
        white = GamePlayer(white, Location.BLACK, white_timer)
        return cls(black, white, challenge.width, challenge.height)
