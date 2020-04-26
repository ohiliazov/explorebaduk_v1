from explorebaduk.database import DatabaseHandler
from explorebaduk.server import PLAYERS, CHALLENGES, GAMES


async def handle_info_players(ws):
    players = ",".join(map(str, PLAYERS.values())) or "null"
    await ws.send(f"players all {players}")


async def handle_info_challenges(ws):
    challenges = ",".join(map(str, CHALLENGES)) or "null"
    await ws.send(f"challenges all {challenges}")


async def handle_info_games(ws):
    games = ",".join(map(str, GAMES)) or "null"
    await ws.send(f"games all {games}")
