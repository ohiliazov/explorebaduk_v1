import asyncio
import json
import random

import websockets

from explorebaduk.crud import get_players_list

lock = asyncio.Lock()

# These users will not be emulated
USER_IDS = [1, 2, 3]
RANDOM_USERS = 5
GUEST_NUMBER = 5


async def players_feed(token):
    async with lock:
        ws = await websockets.connect("ws://localhost:8080/ws")
        await ws.send(
            json.dumps({"event": "authorize", "data": token.token if token else ""}),
        )

    while True:
        try:
            message = await asyncio.wait_for(ws.recv(), timeout=0.5)
            print(f"user_{token.user_id if token else 'guest'} :: {message}")
        except asyncio.TimeoutError:
            pass


async def run():
    all_players = get_players_list()
    players = []
    if USER_IDS:
        players = [player for player in players if player.user_id in USER_IDS]
        for player in all_players:
            players.append(player)
            all_players.remove(player)

    if RANDOM_USERS:
        players.extend(random.sample(all_players, min(RANDOM_USERS, len(all_players))))

    tokens = []
    for player in players:
        for token in player.tokens:
            if token.is_active():
                tokens.append(token)

    if GUEST_NUMBER:
        tokens.extend([None for _ in range(GUEST_NUMBER)])

    await asyncio.gather(*[players_feed(token) for token in tokens])


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run())
