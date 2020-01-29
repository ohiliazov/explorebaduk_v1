import numpy as np

from explorebaduk.gameplay.board import Board, Location, IllegalMoveError
from explorebaduk.gameplay.sgflib import Property, Node
from explorebaduk.utils.sgf import sgf_coord_to_int, int_coord_to_sgf, create_new_sgf


class Kifu:
    def __init__(self, width: int, height: int, handicap: int, komi: float, turn: str = "B"):
        self._shape = (width, height)
        self._turn = turn
        self.cursor = create_new_sgf(width, height, handicap, komi)
        self.board = self.get_root_board()

    def get_root_board(self) -> Board:
        root_node = self.cursor.root_node
        black = root_node.get("AB") or []
        white = root_node.get("AW") or []

        board = np.zeros(self._shape, dtype=int)

        for stone in black:
            coord = sgf_coord_to_int(stone)
            board[coord] = Location.BLACK

        for stone in white:
            coord = sgf_coord_to_int(stone)
            board[coord] = Location.WHITE

        return Board(self._shape, board)

    def add_comment(self, new_comment: str):
        self.cursor.node.add_comment(new_comment)

    def play_move(self, turn, coord) -> None:
        try:
            self.board.move(coord)
        except IllegalMoveError as err:
            raise err

        if coord != "pass":
            coord = int_coord_to_sgf(coord)

        move_prop = Property(turn, [coord])
        node = Node([move_prop])

        self.cursor.append_node(node)
        self.cursor.next()

        return self.board.current
