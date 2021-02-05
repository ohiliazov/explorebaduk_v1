import asyncio
import json

import websockets

lock = asyncio.Lock()

# Add valid tokens here
# Non-valid tokens will result in connection as guest
AUTH_TOKENS = [
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ000000023027",
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ000000023029",
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ000000023032",
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ000000023037",
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ000000023042",
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
    await asyncio.gather(*[players_feed(token) for token in AUTH_TOKENS])


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run())
