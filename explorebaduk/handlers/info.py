import asyncio
from explorebaduk.server import PLAYERS, CHALLENGES, GAMES


async def handle_info_players(ws, data):
    players = ",".join(map(str, PLAYERS.values())) or "null"
    await ws.send(f"players all {players}")


async def handle_info_challenges(ws, data):
    challenges = ",".join(map(str, CHALLENGES)) or "null"
    await ws.send(f"challenges all {challenges}")


async def handle_info_games(ws, data):
    games = ",".join(map(str, GAMES)) or "null"
    await ws.send(f"games all {games}")
