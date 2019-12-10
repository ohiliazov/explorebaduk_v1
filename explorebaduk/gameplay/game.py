import numpy as np

from explorebaduk.gameplay import Board, Location, IllegalMoveError
from explorebaduk.gameplay.sgflib import Property, Node
from explorebaduk.utils.sgf import sgf_coord_to_int, int_coord_to_sgf, create_new_sgf


class Game:
    def __init__(self, shape: tuple = (19, 19), turn: str = 'B'):
        self._shape = shape
        self._turn = turn
        self.cursor = create_new_sgf(shape)
        self.board = self.get_root_board()

    def get_root_board(self) -> Board:
        root_node = self.cursor.root_node
        black = root_node.get('AB') or []
        white = root_node.get('AW') or []

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

        move_prop = Property(turn, [int_coord_to_sgf(coord)])
        node = Node([move_prop])
        self.cursor.append_node(node)
        self.cursor.next()

        return self.board.current


g = Game()
print(g.board)
g.play_move('B', (0, 1))
print(g.board)
print(g.cursor.game.mainline())
