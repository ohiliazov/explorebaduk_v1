from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def values(cls):
        return [item.value for item in cls]


class Target(Enum):
    USER = 'user'
    CHAT = 'chat'
    CHALLENGE = 'challenge'


class UserAction(Enum):
    LOGIN = 'login'
    LOGOUT = 'logout'


class ChallengeAction(Enum):
    CREATE = 'create'
    ACCEPT = 'accept'
    DECLINE = 'decline'
    REVISE = 'revise'
