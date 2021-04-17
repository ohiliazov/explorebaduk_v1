import random
from typing import Union

from ..schemas import (
    Absolute,
    Byoyomi,
    Canadian,
    Color,
    Fischer,
    GameRequest,
    Unlimited,
)
from ..sgftree import Kifu
from ..utils.timer import (
    AbsoluteTimer,
    ByoyomiTimer,
    CanadianTimer,
    FischerTimer,
    Timer,
    UnlimitedTimer,
)


def timer(
    time_settings: Union[Unlimited, Absolute, Byoyomi, Canadian, Fischer],
) -> Timer:
    if isinstance(time_settings, Absolute):
        return AbsoluteTimer(main_time=time_settings.main_time)

    if isinstance(time_settings, Byoyomi):
        return ByoyomiTimer(
            main_time=time_settings.main_time,
            overtime=time_settings.overtime,
            periods=time_settings.periods,
        )

    if isinstance(time_settings, Canadian):
        return CanadianTimer(
            main_time=time_settings.main_time,
            overtime=time_settings.overtime,
            stones=time_settings.stones,
        )

    if isinstance(time_settings, Fischer):
        return FischerTimer(
            main_time=time_settings.main_time,
            bonus=time_settings.bonus,
        )

    return UnlimitedTimer()


class Game:
    def __init__(self, user_id: int, opponent_id: int, game_setup: GameRequest):
        self.game_setup = game_setup
        self.black_id, self.white_id = self.get_colors(user_id, opponent_id)
        self.kifu = Kifu(
            game_setup.board_size,
            game_setup.game_settings.handicap,
            game_setup.game_settings.komi,
        )
        self.black_timer = timer(game_setup.time_settings)
        self.white_timer = timer(game_setup.time_settings)

    def get_colors(self, user_id: int, opponent_id: int):
        if self.game_setup.game_settings.color == Color.BLACK:
            return user_id, opponent_id
        elif self.game_setup.game_settings.color == Color.WHITE:
            return opponent_id, user_id
        else:
            return random.sample([user_id, opponent_id], 2)
