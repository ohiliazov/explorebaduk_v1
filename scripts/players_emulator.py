import asyncio
import json

import websockets

# Add valid tokens here
# Non-valid tokens will result in connection as guest
AUTH_TOKENS = [
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ000000000001",
    "4b038200073462e8eae28cdc1515d655ea19ba07",
]


async def players_feed(token):
    ws = await websockets.connect("ws://localhost:8080/players")
    if token:
        await ws.send(json.dumps({"event": "authorize", "data": {"token": token}}))

    while True:
        try:
            message = await asyncio.wait_for(ws.recv(), timeout=0.5)
            print(f"{token} :: {message}")
        except asyncio.TimeoutError:
            pass


async def run():
    await asyncio.gather(*[players_feed(token) for token in AUTH_TOKENS])


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run())
