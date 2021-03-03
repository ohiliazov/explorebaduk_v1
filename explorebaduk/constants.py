from enum import Enum


class Color(str, Enum):
    BLACK = "black"
    WHITE = "white"
    NIGIRI = "nigiri"


class TimeSystem(str, Enum):
    UNLIMITED = "unlimited"
    ABSOLUTE = "absolute"
    BYOYOMI = "byo-yomi"
    CANADIAN = "canadian"
    FISCHER = "fischer"


class GameCategory(str, Enum):
    REAL_TIME = "real-time"
    CORRESPONDENCE = "correspondence"


class RuleSet(str, Enum):
    JAPANESE = "japanese"
    CHINESE = "chinese"
