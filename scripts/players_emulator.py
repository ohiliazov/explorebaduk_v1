import asyncio
import random

import websockets

from explorebaduk.database import DatabaseHandler
from explorebaduk.dependencies import create_token

lock = asyncio.Lock()

# These users will not be emulated
INCLUDE_USER_IDS = [1, 2, 3]
EXCLUDE_USER_IDS = [4, 5, 6]
RANDOM_USERS = 2
GUEST_NUMBER = 1


async def players_feed(token, user):
    async with lock:
        ws = await websockets.connect("ws://localhost:8080/ws")
        await ws.send(token)
    if token:
        print("Authorization token:", token)
    while True:
        try:
            message = await asyncio.wait_for(ws.recv(), timeout=0.5)
            print(f"user_{user.username if user else 'guest'} :: {message}")
        except asyncio.TimeoutError:
            pass


async def run():
    with DatabaseHandler() as db:
        all_players = db.get_users()

    players = []

    for player in all_players:
        if player.user_id in EXCLUDE_USER_IDS:
            all_players.remove(player)
        if player.user_id in INCLUDE_USER_IDS:
            players.append(player)
            all_players.remove(player)

    if RANDOM_USERS:
        players.extend(random.sample(all_players, min(RANDOM_USERS, len(all_players))))

    tokens = []
    for player in players:
        tokens.append((create_token(player), player))

    if GUEST_NUMBER:
        tokens.extend([("", None) for _ in range(GUEST_NUMBER)])

    await asyncio.gather(*[players_feed(token, user) for token, user in tokens])


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run())
