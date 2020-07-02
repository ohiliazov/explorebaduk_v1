from explorebaduk.server import USERS, CHALLENGES, GAMES


async def handle_info_players(ws, *args):
    players = ",".join(map(str, [user for user in USERS.values() if user])) or "null"
    await ws.send(f"players all {players}")


async def handle_info_challenges(ws, *args):
    challenges = ",".join(map(str, CHALLENGES)) or "null"
    await ws.send(f"challenges all {challenges}")


async def handle_info_games(ws, *args):
    games = ",".join(map(str, GAMES)) or "null"
    await ws.send(f"games all {games}")
