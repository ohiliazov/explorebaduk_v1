from .board import Board
from .constants import APP_NAME, APP_VERSION, HANDICAP_SGF_COORDINATES
from .properties import GoLabel, RootLabel
from .sgflib import GameTree, Node, Property
from .utils import sgf_coord_to_int


class Kifu:
    def __init__(self, board_size: int, handicap: int = 0, komi: float = 7.5):
        self.cursor = self.make_game_tree(board_size, handicap, komi)
        self.board = Board((board_size, board_size), handicap=handicap)
        self.scoring_board = None

    @property
    def turn(self):
        return self.board.turn_color

    def __str__(self):
        return str(self.cursor.game)

    @property
    def turn_label(self):
        return "B" if self.turn == "black" else "W"

    @property
    def time_label(self):
        return "BL" if self.turn == "black" else "WL"

    def make_game_tree(self, size: int, handicap: int = 0, komi: float = 6.5):
        root_properties = [
            Property(RootLabel.FILE_FORMAT.value, ["4"]),
            Property(RootLabel.GAME_TYPE.value, ["1"]),
            Property(RootLabel.APPLICATION.value, [f"{APP_NAME}:{APP_VERSION}"]),
            Property(RootLabel.CHARSET.value, ["UTF-8"]),
            Property(RootLabel.BOARD_SIZE.value, [size]),
            Property(GoLabel.HANDICAP.value, [handicap]),
            Property(GoLabel.KOMI.value, [komi]),
        ]

        if handicap:
            root_properties.append(Property("AB", HANDICAP_SGF_COORDINATES[handicap]))
        game_tree = GameTree([Node(root_properties)])

        return game_tree.cursor()

    def load_sgf(self):
        raise NotImplementedError("To be done")

    def is_valid_move(self, coord):
        return bool(self.board.legal_moves[sgf_coord_to_int(coord)])

    def make_move(self, coord: str, time_left: float = 0.0):
        self.scoring_board = None
        move_value = [] if coord == "pass" else [coord]
        node = Node(
            [
                Property(self.turn_label, move_value),
                Property(self.time_label, [f"{time_left:.2f}"]),
            ],
        )

        if move_value:
            self.board.move(sgf_coord_to_int(coord))
        else:
            self.board.make_pass()

        self.cursor.append_node(node, is_main=True)
        self.cursor.next()

    def undo(self):
        self.scoring_board = None
        self.board.undo()
        self.cursor.previous()

    def get_score(self, rules="japanese"):
        if not self.scoring_board:
            self.scoring_board = self.board.get_scoring_board()

        if rules == "japanese":
            return self.scoring_board.japanese_score
        else:
            return self.scoring_board.chinese_score

    def mark_stone(self, action, coord):
        if self.scoring_board is None:
            self.scoring_board = self.board.get_scoring_board()

        if action == "dead":
            self.scoring_board.mark_dead(coord)
        else:
            self.scoring_board.mark_alive(coord)

        return self.get_score()
