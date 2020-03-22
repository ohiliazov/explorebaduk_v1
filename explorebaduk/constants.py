from enum import IntEnum


# Time to wait for match making
AUTO_MATCH_DELAY = 3

# Delay before making a move
MOVE_DELAY = 1


class GameType(IntEnum):
    RANKED = 0
    FREE = 1
    DEMO = 2
    RENGO = 3


class Ruleset(IntEnum):
    CHINESE = 0
    JAPANESE = 1
    AGA = 2
    ING = 3
    NEW_ZEALAND = 4


class TimeSystem(IntEnum):
    NO_TIME = 0
    ABSOLUTE = 1
    BYOYOMI = 2
    CANADIAN = 3
    FISCHER = 4


class PlayerColor(IntEnum):
    AUTO = 0
    NIGIRI = 1
    BLACK = 2
    WHITE = 3


DEFAULT_RULESET = Ruleset.CHINESE
DEFAULT_KOMI = 7.5
