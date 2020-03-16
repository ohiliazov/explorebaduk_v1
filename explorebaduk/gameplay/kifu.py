import numpy as np

from explorebaduk.gameplay.board import Board, Location, IllegalMoveError
from explorebaduk.gameplay.sgflib import Property, Node
from explorebaduk.utils.sgf import sgf_coord_to_int, create_new_sgf


class Kifu:
    def __init__(self, width: int, height: int, handicap: int = 0, komi: float = 7.5):
        self._shape = (width, height)
        self.cursor = create_new_sgf(width, height, handicap, komi)
        self.board = self.get_root_board()
        self.history = []

    @property
    def turn_color(self):
        return "black" if self.board.turn is Location.BLACK else "white"

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

    def play_move(self, color: str, coord: str, flip_turn: bool = True) -> None:
        if color != self.turn_color:
            raise IllegalMoveError("Invalid move order")

        self.board.move(sgf_coord_to_int(coord), flip_turn)

        turn_label = "B" if color == "black" else "W"

        move_prop = Property(turn_label, [coord])
        node = Node([move_prop])

        self.cursor.append_node(node)
        self.cursor.next()

        self.history.append(coord)

        return self.board.current

    def make_pass(self, color: str) -> None:
        if color != self.turn_color:
            raise IllegalMoveError("Invalid move order")

        self.board.make_pass()

        coord = ""
        turn_label = "B" if color == "black" else "W"

        move_prop = Property(turn_label, [coord])
        node = Node([move_prop])

        self.cursor.append_node(node)
        self.cursor.next()

        self.history.append("pass")

        return self.board.current
