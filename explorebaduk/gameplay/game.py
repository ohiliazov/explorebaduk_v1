import random

from sgftree import Kifu

from ..schemas import Color, GameSetup


class Game:
    def __init__(self, user_id: int, opponent_id: int, game_setup: GameSetup):
        self.game_setup = game_setup
        self.black_id, self.white_id = self.get_colors(user_id, opponent_id)
        self.kifu = Kifu(game_setup.board_size)

    def get_colors(self, user_id: int, opponent_id: int):
        if self.game_setup.game_settings.color == Color.BLACK:
            return user_id, opponent_id
        elif self.game_setup.game_settings.color == Color.WHITE:
            return opponent_id, user_id
        else:
            return random.sample([user_id, opponent_id], 2)
