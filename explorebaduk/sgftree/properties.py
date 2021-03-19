from enum import Enum


class MoveLabel(Enum):
    BLACK = "B"
    WHITE = "W"
    ILLEGAL = "KO"
    MOVE_NUMBER = "MN"


class SetupLabel(Enum):
    BLACK = "AB"
    WHITE = "AW"
    EMPTY = "AE"
    TURN = "PL"


class NodeAnnotationLabel(Enum):
    COMMENT = "C"
    EVEN = "DM"
    GOOD_FOR_BLACK = "GB"
    GOOD_FOR_WHITE = "GW"
    HOTSPOT = "HO"
    NAME = "N"
    UNCLEAR = "UC"
    NODE_VALUE = "V"


class MoveAnnotationLabel(Enum):
    BAD = "BM"
    DOUBTFUL = "DO"
    INTERESTING = "IT"
    TESUJI = "TE"


class MarkupLabel(Enum):
    ARROW = "AR"
    CIRCLE = "CR"
    DIM = "DD"
    LABEL = "LB"
    LINE = "LN"
    MARK = "MA"
    SELECTED = "SL"
    SQUARE = "SQ"
    TRIANGLE = "TR"


class RootLabel(Enum):
    APPLICATION = "AP"
    CHARSET = "CA"
    FILE_FORMAT = "FF"
    GAME_TYPE = "GM"
    STYLE = "ST"
    BOARD_SIZE = "SZ"


class GameInfoLabel(Enum):
    COMMENTATOR = "AN"
    BLACK_RANK = "BR"
    BLACK_TEAM = "BT"
    COPYRIGHT = "CP"
    DATE = "DT"
    EVENT = "EV"
    GAME_NAME = "GN"
    GAME_COMMENT = "GC"
    OPENING = "ON"
    OVERTIME = "OT"
    PLAYER_BLACK = "PB"
    PLACE = "PC"
    PLAYER_WHITE = "PW"
    RESULT = "RE"
    ROUND = "RO"
    RULES = "RU"
    SOURCE = "SO"
    TIME = "TM"
    USER = "US"
    WHITE_RANK = "WR"
    WHITE_TEAM = "WT"


class TimingLabel(Enum):
    BLACK_TIME_LEFT = "BL"
    BLACK_MOVES_LEFT = "OB"
    WHITE_MOVES_LEFT = "OW"
    WHITE_TIME_LEFT = "WL"


class MiscellaneousLabel(Enum):
    FIGURE = "FG"
    PRINT_MODE = "PM"
    BOARD_VIEW = "VW"


class GoLabel(Enum):
    HANDICAP = "HA"
    KOMI = "KM"
    TERRITORY_BLACK = "TB"
    TERRITORY_WHITE = "TW"
