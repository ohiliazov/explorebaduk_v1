from enum import Enum, IntEnum


# Time to wait for match making
AUTO_MATCH_DELAY = 3

# Message result statuses
ERROR = "error"


class MessageType(Enum):
    SYNC = "sync"
    AUTH = "auth"
    CHALLENGE = "challenge"


class LoginAction(Enum):
    LOGIN = "login"
    LOGOUT = "logout"


class ChallengeAction(Enum):
    NEW = "new"
    UPDATE = "update"
    CANCEL = "cancel"
    JOIN = "join"
    LEAVE = "leave"
    ACCEPT = "accept"
    DECLINE = "decline"
    REVISE = "revise"
    RETURN = "return"


class GameType(IntEnum):
    RANKED = 0
    FREE = 1
    DEMO = 2
    RENGO = 3


class Ruleset(IntEnum):
    JAPANESE = 0
    CHINESE = 1
    AGA = 2
    ING = 3
    NEW_ZEALAND = 4


class TimeSystem(IntEnum):
    NO_TIME = 0
    ABSOLUTE = 1
    BYOYOMI = 2
    CANADIAN = 3
    FISCHER = 4
    CUSTOM = 5


class RequestStatus(IntEnum):
    JOINED = 0
    CHANGED = 1
    RETURNED = 2
    ACCEPTED = 3
