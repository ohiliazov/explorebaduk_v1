import numpy as np

from sgftree import Property, Node
from sgftree.board import Board, Location

from explorebaduk.utils.sgf import sgf_coord_to_int, create_new_sgf


class KifuBoard:
    def __init__(self, width: int, height: int, handicap: int = 0, komi: float = 7.5):
        self._shape = (width, height)
        self.cursor = create_new_sgf((width, height), handicap, komi)
        self.board = Board((width, height))
        self.history = []
        self.board.update_board(self.cursor.root_node.setup_props["AB"],
                                self.cursor.root_node.setup_props["AW"])

    @property
    def turn_color(self):
        return "black" if self.board.turn is Location.BLACK else "white"

    @property
    def turn_label(self):
        return "B" if self.board.turn is Location.BLACK else "W"

    @property
    def time_label(self):
        return "BL" if self.board.turn is Location.BLACK else "WL"

    def play_move(self, coord: str, time_left: float = 0.0, flip_turn: bool = True) -> np.ndarray:
        node = Node([
            Property(self.turn_label, [coord]),
            Property(self.time_label, [f"{time_left:.2f}"])
        ])

        self.board.move(sgf_coord_to_int(coord), flip_turn)
        self.history.append(coord)

        self.cursor.append_node(node)
        self.cursor.next()

        return self.board.board

    def make_pass(self, time_left: float = 0.0) -> np.ndarray:
        node = Node([
            Property(self.turn_label, []),
            Property(self.time_label, [f"{time_left:.2f}"])
        ])
        self.board.make_pass()
        self.history.append("pass")

        self.cursor.append_node(node)
        self.cursor.next()

        return self.board.board

    def undo(self):
        self.board.undo()
        self.cursor.previous()
