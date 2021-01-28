APP_NAME = "ExploreBaduk"


class RouteName:
    CHALLENGES_VIEW = "Challenges View"
    PLAYERS_FEED = "PLayers Feed"
    CHALLENGES_FEED = "Challenges List Feed"
    CHALLENGE_FEED = "Challenge Feed"


class EventName:
    AUTHORIZE = "authorize"
    ERROR = "error"

    PLAYERS_ADD = "players.add"
    PLAYERS_REMOVE = "players.remove"

    CHALLENGES_ADD = "challenges.add"
    CHALLENGES_REMOVE = "challenges.remove"

    CHALLENGE_SET = "challenge.set"
    CHALLENGE_UNSET = "challenge.unset"
    CHALLENGE_JOIN = "challenge.join"
    CHALLENGE_LEAVE = "challenge.leave"


ALLOWED_GAME_TYPES = ["ranked", "free"]
ALLOWED_RULES = ["japanese", "chinese"]
ALLOWED_HANDICAP_STONES = [0, 2, 3, 4, 5, 6, 7, 8, 9]
ALLOWED_TIME_SYSTEMS = ["unlimited", "absolute", "byo-yomi", "canadian", "fischer"]
