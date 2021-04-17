from enum import Enum


class TimeSystem(str, Enum):
    UNLIMITED = "unlimited"
    ABSOLUTE = "absolute"
    BYOYOMI = "byo-yomi"
    CANADIAN = "canadian"
    FISCHER = "fischer"


class GameType(str, Enum):
    RANKED = "ranked"
    FREE = "free"
    TEACHING = "teaching"
