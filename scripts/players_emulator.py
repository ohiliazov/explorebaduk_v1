import asyncio
import json

import websockets

from explorebaduk.crud import get_players_list

lock = asyncio.Lock()

# These users will not be emulated
EXCLUDE_USER_IDS = [
    1,
    2,
    3,
]


async def players_feed(token):
    async with lock:
        ws = await websockets.connect("ws://localhost:8080/ws")
        if token:
            await ws.send(json.dumps({"event": "authorize", "data": token}))

    while True:
        try:
            message = await asyncio.wait_for(ws.recv(), timeout=0.5)
            print(f"{token} :: {message}")
        except asyncio.TimeoutError:
            pass


async def run():
    players = [
        player
        for player in get_players_list()
        if player.user_id not in EXCLUDE_USER_IDS
    ]
    print(players)
    tokens = []
    for player in players:
        for token in player.tokens:
            if token.is_active():
                tokens.append(token.token)

    tokens.extend(["", "", "", "", ""])
    await asyncio.gather(*[players_feed(token) for token in tokens])


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run())
