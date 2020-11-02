import asyncio
import select
import sys
import string

import websockets

preset_messages = {}


def process_message():
    message = sys.stdin.readline().strip()

    for cmd, message_func in preset_messages.items():
        if message.startswith(cmd):
            _, *data = message.split(" ", maxsplit=1)
            message = message_func(*data)

    return message


async def players_feed(token, ws_path: str):
    uri = f"ws://localhost:8080/{ws_path}"
    async with websockets.connect(uri, extra_headers={"Authorization": token}) as ws:
        while True:
            try:
                while True:
                    response = await asyncio.wait_for(ws.recv(), timeout=0.5)
                    print("<", response)
            except asyncio.TimeoutError:
                pass

            read_list, *_ = select.select([sys.stdin], [], [], 0.5)

            if read_list:
                await ws.send(process_message())


if __name__ == "__main__":
    user_id = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 1
    ws_path = sys.argv[2] if len(sys.argv) > 2 else "players_feed"
    token = f"{string.ascii_letters}{user_id:012d}"
    asyncio.get_event_loop().run_until_complete(players_feed(token, ws_path))
