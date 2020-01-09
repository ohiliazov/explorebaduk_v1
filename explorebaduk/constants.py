from enum import IntEnum


# Message result statuses
OK = 'ok'
ERROR = 'error'

# Authentication
AUTH = 'auth'
LOGIN = 'login'
LOGOUT = 'logout'

# Challenge
CHALLENGE = 'challenge'

# Step 0. Create challenge
NEW_CHALLENGE = 'new'  # TODO

# Step 1. Update or cancel (by creator)
UPDATE_CHALLENGE = 'update'  # TODO
CANCEL_CHALLENGE = 'cancel'  # TODO

# Step 2. Join or leave challenge (by joined player)
JOIN_CHALLENGE = 'join'  # TODO
LEAVE_CHALLENGE = 'leave'  # TODO

# Step 3. Accept, decline or return joined player (by creator)
ACCEPT_JOINED = 'accept'  # TODO
DECLINE_JOINED = 'decline'  # TODO
EDIT_JOINED = 'edit'  # TODO

# Step 4. Accept returned challenge (by joined player)
ACCEPT_EDITS = 'accept_edits'  # TODO
REVISE_EDITS = 'revise_edits'  # TODO

# Game
PLAY = 'play'
UNDO = 'undo'


# challenge statuses
REQUESTED = 'requested'
ACCEPTED = 'accepted'
CHANGED = 'changed'
RETURNED = 'returned'


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
