# Message result statuses
OK = 'ok'
ERROR = 'error'

# Authorization
LOGIN = 'login'
LOGOUT = 'logout'

AUTH_ACTIONS = [LOGIN, LOGOUT]

# CHALLENGE
# Step 0. Create challenge
CREATE_CHALLENGE = 'create_challenge'

# Step 1. Update or cancel (by creator)
UPDATE_CHALLENGE = 'update_challenge'
CANCEL_CHALLENGE = 'cancel_challenge'

# Step 2. Join or leave challenge (by joined player)
JOIN_CHALLENGE = 'join_challenge'
LEAVE_CHALLENGE = 'leave_challenge'

# Step 3. Accept, decline or return joined player (by creator)
ACCEPT_JOINED = 'accept_joined'
DECLINE_JOINED = 'decline_joined'
RETURN_JOINED = 'return_joined'

# Step 4. Accept returned challenge (by joined player)
ACCEPT_RETURN = 'accept_return'

CHALLENGE_ACTIONS = [CREATE_CHALLENGE, UPDATE_CHALLENGE, CANCEL_CHALLENGE,
                     JOIN_CHALLENGE, LEAVE_CHALLENGE,
                     ACCEPT_JOINED, DECLINE_JOINED, RETURN_JOINED,
                     ACCEPT_RETURN]

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
