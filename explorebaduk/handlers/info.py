import asyncio
from explorebaduk.server import PLAYERS, CHALLENGES, GAMES


async def handle_info_players(ws, data):
    if PLAYERS:
        return await asyncio.gather(*[ws.send(f"info players {player}") for player in PLAYERS.values()])


async def handle_info_challenges(ws, data):
    if CHALLENGES:
        return await asyncio.gather(*[ws.send(f"info challenges {challenge}") for challenge in CHALLENGES])


async def handle_info_games(ws, data):
    if GAMES:
        return await asyncio.gather(*[ws.send(f"info games {game}") for game in GAMES.values()])
