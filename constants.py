from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def values(cls):
        return [item.value for item in cls]


class Target(ExtendedEnum):
    AUTH = 'auth'
    CHAT = 'chat'
    CHALLENGE = 'challenge'
    PLAY = 'play'


class AuthAction(ExtendedEnum):
    LOGIN = 'login'
    LOGOUT = 'logout'


class ChatAction(ExtendedEnum):
    SEND_MESSAGE = 'send'


class ChallengeAction(ExtendedEnum):
    CREATE = 'create'
    ACCEPT = 'accept'
    REVISE = 'revise'
    DECLINE = 'decline'


class GameTypes(Enum):
    RANKED = 'ranked'
    FREE = 'free'
    TEACHING = 'teaching'
    DEMO = 'demo'
    SIMULTANEOUS = 'simultaneous'
    BLIND = 'blind-go'
    ONE_COLOR = 'one-color-go'
    RENGO = 'rengo'


class Rulesets(Enum):
    CHINESE = 'Chinese Rules'
    JAPANESE = 'Japanese Rules'
    AGA = 'AGA Rules'
    ING = 'Ing Rules'
    NEW_ZEALAND = 'New Zealand Rules'
