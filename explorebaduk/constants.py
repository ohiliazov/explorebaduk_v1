from enum import IntEnum


# Message result statuses
OK = 'ok'
ERROR = 'error'

# Authentication
LOGIN = 'login'
LOGOUT = 'logout'

# Challenge
CHALLENGE = 'challenge'

# Step 0. Create challenge
CREATE_CHALLENGE = 'create'  # TODO

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

CHALLENGE_ACTIONS = [
    CREATE_CHALLENGE, UPDATE_CHALLENGE, CANCEL_CHALLENGE,
    JOIN_CHALLENGE, LEAVE_CHALLENGE,
    ACCEPT_JOINED, DECLINE_JOINED, EDIT_JOINED,
    ACCEPT_EDITS, REVISE_EDITS
]

# Game
PLAY = 'play'
UNDO = 'undo'


# challenge statuses
REQUESTED = 'requested'
ACCEPTED = 'accepted'
CHANGED = 'changed'
RETURNED = 'returned'

# Time settings
NO_TIME = 'no_time'
ABSOLUTE = 'absolute'
BYOYOMI = 'byoyomi'
CANADIAN = 'canadian'
FISCHER = 'fischer'
CUSTOM = 'custom'

VALID_TIME_SETTINGS = [NO_TIME, ABSOLUTE, BYOYOMI, CANADIAN, FISCHER, CUSTOM]


class GameType(IntEnum):
    RANKED = 0
    FREE = 1
    DEMO = 2
    TEACHING = 3
    SIMULTANEOUS = 4
    BLIND = 5
    ONE_COLOR = 6
    RENGO = 7


class Ruleset(IntEnum):
    JAPANESE = 0
    CHINESE = 1
    AGA = 2
    ING = 3
    NEW_ZEALAND = 4
