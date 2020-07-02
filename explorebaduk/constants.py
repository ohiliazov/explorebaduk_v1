from enum import Enum, IntEnum

# Delay before making a move
MOVE_DELAY = 1


class GameType:
    RANKED = "ranked"
    FREE = "free"


class GameRules(Enum):
    CHINESE = "chinese"
    JAPANESE = "japanese"


class TimeSystem(IntEnum):
    NO_TIME = 0
    ABSOLUTE = 1
    BYOYOMI = 2
    CANADIAN = 3
    FISCHER = 4


PASS = "pass"
RESIGN = "resign"
