from enum import Enum


class Action(Enum):
    LOGIN = 'login'
    CHALLENGE = 'challenge'
    CHAT = 'chat'
    PLAY = 'play'


class ChallengeAction(Enum):
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
