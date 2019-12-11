# Time settings
NO_TIME = 'no_time'
ABSOLUTE = 'absolute'
BYOYOMI = 'byoyomi'
CANADIAN = 'canadian'
FISCHER = 'fischer'
CUSTOM = 'custom'

VALID_TIME_SETTINGS = [NO_TIME, ABSOLUTE, BYOYOMI, CANADIAN, FISCHER, CUSTOM]

# User actions
LOGIN = 'login'
LOGOUT = 'logout'

AUTH_ACTIONS = [LOGIN, LOGOUT]

# Challenge actions
CHALLENGE_CREATE = 'new'
CHALLENGE_CANCEL = 'cancel'
CHALLENGE_ACCEPT = 'accept'
CHALLENGE_DECLINE = 'decline'
CHALLENGE_RETURN = 'return'
CHALLENGE_START = 'start'

CHALLENGE_ACTIONS = [CHALLENGE_CREATE, CHALLENGE_ACCEPT, CHALLENGE_DECLINE, CHALLENGE_REVISE]

OK = 'ok'
ERROR = 'error'

# challenge statuses
REQUESTED = 'requested'
ACCEPTED = 'accepted'
CHANGED = 'changed'
RETURNED = 'returned'
