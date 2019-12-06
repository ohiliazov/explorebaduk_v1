# Targets
TARGET_USER = 'user'
TARGET_CHALLENGE = 'challenge'

VALID_TARGETS = [
    TARGET_USER,
    TARGET_CHALLENGE,
]

# User actions
USER_LOGIN = 'login'
USER_LOGOUT = 'logout'

# Challenge actions
CHALLENGE_NEW = 'new'
CHALLENGE_ACCEPT = 'accept'
CHALLENGE_DECLINE = 'decline'
CHALLENGE_REVISE = 'revise'

VALID_ACTIONS = {
    TARGET_USER: [
        USER_LOGIN,
        USER_LOGOUT,
    ],
    TARGET_CHALLENGE: [
        CHALLENGE_NEW,
        CHALLENGE_ACCEPT,
        CHALLENGE_DECLINE,
        CHALLENGE_REVISE,
    ]
}
