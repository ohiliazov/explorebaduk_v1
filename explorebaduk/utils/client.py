import asyncio
import json
import string
import websockets
import sys, select


def login_message(user_id: int = 1):
    return f"auth login {user_id} {string.ascii_letters}{user_id:012d}"


logout_message = "auth logout"


challenge_message = "challenge new GT0RL0PL2 19:19 F000 T0M3600O0P0S0B0D0"
challenge_message_bad = "challenge new GT0RL0PL2 55:19 F000 T0M3600O0P0S0B0D0"

join_message = "challenge join 1"

challenge_cancel_message = "challenge cancel 1"


async def hello():
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                    print('<', response)
            except asyncio.TimeoutError:
                pass

            read_list, *_ = select.select([sys.stdin], [], [], 0.5)

            if read_list:
                message = sys.stdin.readline().strip()
                if message.startswith('login'):
                    user_id = message.split(' ')[-1]
                    user_id = int(user_id) if user_id.isdigit() else 1
                    await websocket.send(login_message(user_id))
                elif message == 'logout':
                    await websocket.send(logout_message)
                elif message == 'challenge':
                    await websocket.send(challenge_message)
                elif message == 'challenge bad':
                    await websocket.send(challenge_message_bad)
                elif message == 'join':
                    await websocket.send(json.dumps(join_message))
                elif message == 'cancel':
                    await websocket.send(json.dumps(challenge_message))
                else:
                    await websocket.send(message)

asyncio.get_event_loop().run_until_complete(hello())
