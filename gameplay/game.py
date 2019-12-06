import numpy as np

from gameplay.board import Board, Location
from utils.sgf import sgf_coord_to_int, create_new_sgf


class Game:
    def __init__(self, size: int = 19):
        self._size = size
        self.cursor = create_new_sgf(size)
        self.board = self.get_root_board()

    def get_root_board(self) -> Board:
        root_node = self.cursor.root_node
        black = root_node.get('AB').data
        white = root_node.get('AW').data

        board = np.zeros(self._size, dtype=int)

        for stone in black:
            coord = sgf_coord_to_int(stone)
            board[coord] = Location.BLACK

        for stone in white:
            coord = sgf_coord_to_int(stone)
            board[coord] = Location.WHITE

        return Board(self._size, board)

    def add_comment(self, new_comment: str):
        self.cursor.node.add_comment(new_comment)
