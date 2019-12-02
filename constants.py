from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def values(cls):
        return [item.value for item in cls]


class Target(Enum):
    AUTH = 'auth'
    CHAT = 'chat'
    CHALLENGE = 'challenge'


class AuthAction(Enum):
    LOGIN = 'login'
    LOGOUT = 'logout'


class ChatAction(Enum):
    NEW = 'new'


class ChallengeAction(Enum):
    CREATE = 'create'
    ACCEPT = 'accept'
    DECLINE = 'decline'
    REVISE = 'revise'


TARGET_ACTIONS = {
    Target.AUTH: AuthAction,
    Target.CHAT: ChatAction,
    Target.CHALLENGE: ChallengeAction,
}
