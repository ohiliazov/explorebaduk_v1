from .board import Board
from .constants import APP_NAME, APP_VERSION, HANDICAP_SGF_COORS
from .properties import GameInfoLabel, GoLabel, RootLabel, SetupLabel
from .sgflib import GameTree, Node, Property
from .utils import sgf_coord_to_int


class Kifu:
    def __init__(
        self,
        date: str,
        rules: str,
        name: str,
        player_black: str,
        black_rank: str,
        player_white: str,
        white_rank: str,
        main_time: int,
        overtime: str,
        board_size: int,
        handicap: int,
        komi: float,
    ):
        self.date = date
        self.rules = rules
        self.name = name
        self.player_black = player_black
        self.black_rank = black_rank
        self.player_white = player_white
        self.white_rank = white_rank

        self.main_time = main_time
        self.overtime = overtime

        self.board_size = board_size
        self.handicap = handicap
        self.komi = komi

        self.handicap_stones = HANDICAP_SGF_COORS[handicap]

        self.cursor = None
        self.board = None
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

    def init(self):
        root_properties = [
            Property(RootLabel.FILE_FORMAT.value, ["4"]),
            Property(RootLabel.GAME_TYPE.value, ["1"]),
            Property(RootLabel.CHARSET.value, ["UTF-8"]),
            Property(RootLabel.APPLICATION.value, [f"{APP_NAME}:{APP_VERSION}"]),
            Property(RootLabel.BOARD_SIZE.value, [self.board_size]),
            Property(GameInfoLabel.PLACE.value, ["explorebaduk.com"]),
            Property(GameInfoLabel.RULES.value, [self.rules]),
            Property(GameInfoLabel.GAME_NAME.value, [self.name]),
            Property(GameInfoLabel.PLAYER_BLACK.value, [self.player_black]),
            Property(GameInfoLabel.BLACK_RANK.value, [self.black_rank]),
            Property(GameInfoLabel.PLAYER_WHITE.value, [self.player_white]),
            Property(GameInfoLabel.WHITE_RANK.value, [self.white_rank]),
            Property(GameInfoLabel.TIME.value, [self.main_time]),
            Property(GameInfoLabel.OVERTIME.value, [self.overtime]),
            Property(GoLabel.HANDICAP.value, [self.handicap]),
            Property(GoLabel.KOMI.value, [self.komi]),
        ]

        if self.handicap:
            root_properties.append(
                Property(SetupLabel.BLACK.value, HANDICAP_SGF_COORS[self.handicap]),
            )

        self.cursor = GameTree([Node(root_properties)]).cursor()
        self.board = Board(
            shape=(self.board_size, self.board_size),
            handicap=self.handicap,
            komi=self.komi,
        )

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
