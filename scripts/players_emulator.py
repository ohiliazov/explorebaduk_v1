import asyncio
import json
import random

import websockets

from explorebaduk.crud import DatabaseHandler

lock = asyncio.Lock()

# These users will not be emulated
INCLUDE_USER_IDS = [1, 2, 3]
EXCLUDE_USER_IDS = [4, 5, 6]
RANDOM_USERS = 2
GUEST_NUMBER = 1


async def players_feed(token):
    async with lock:
        ws = await websockets.connect("ws://localhost:8080/ws")
        await ws.send(
            json.dumps({"event": "authorize", "data": token.token if token else ""}),
        )
    if token:
        print("Authorization token:", token.token)
    while True:
        try:
            message = await asyncio.wait_for(ws.recv(), timeout=0.5)
            print(f"user_{token.user_id if token else 'guest'} :: {message}")
        except asyncio.TimeoutError:
            pass


async def run():
    with DatabaseHandler() as db:
        all_players = [
            player
            for player in db.get_users()
            if any(token.is_active() for token in player.tokens)
        ]

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
        for token in player.tokens:
            if token.is_active():
                tokens.append(token)
                break

    if GUEST_NUMBER:
        tokens.extend([None for _ in range(GUEST_NUMBER)])

    await asyncio.gather(*[players_feed(token) for token in tokens])


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run())
