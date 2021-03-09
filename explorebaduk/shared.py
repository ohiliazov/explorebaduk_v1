from collections import defaultdict

USERS_ONLINE = set()
OPEN_GAMES = {}
OPEN_GAME_REQUESTS = defaultdict(dict)
GAME_INVITES = defaultdict(dict)


class ExploreBadukData:
    user_ids = set()
    open_games = {}
    open_game_requests = defaultdict(dict)
    game_invites = defaultdict(dict)
