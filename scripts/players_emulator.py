import asyncio

import websockets

# Add valid tokens here
# Non-valid tokens will result in connection as guest
AUTH_TOKENS = [
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ000000000001",
    "4b038200073462e8eae28cdc1515d655ea19ba07",
]


async def players_feed(ws):
    while True:
        try:
            message = await asyncio.wait_for(ws.recv(), timeout=0.5)
            print(f"{ws.extra_headers['Authorization']} :: {message}")
        except asyncio.TimeoutError:
            pass


async def run():
    ws_list = await asyncio.gather(
        *[
            websockets.connect("ws://localhost:8080/players", extra_headers={"Authorization": token})
            for token in AUTH_TOKENS
        ]
    )
    await asyncio.gather(*[players_feed(ws) for ws in ws_list])


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run())
