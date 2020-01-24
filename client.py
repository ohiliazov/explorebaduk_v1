import asyncio
import string
import websockets
import sys
import select


def login_message(user_id: str = "1"):
    return f"auth login {user_id} {string.ascii_letters}{int(user_id):012d}"


def new_challenge(game_type: str = "0",):
    pass


def join_challenge(challenge_id: str = "1"):
    return f"challenge join {challenge_id}"


def cancel_challenge(challenge_id: str = "1"):
    return f"challenge cancel {challenge_id}"


preset_messages = {
    "login": login_message,
    "logout": lambda: "auth logout",
    "new": lambda: "challenge new GT0RL0PL2 19:19 F000 T0M3600O0P0S0B0D0",
    "join": join_challenge,
    "cancel": cancel_challenge,
}


async def hello():
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        while True:
            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                    print("<", response)
            except asyncio.TimeoutError:
                pass

            read_list, *_ = select.select([sys.stdin], [], [], 0.5)

            if read_list:
                message = sys.stdin.readline().strip()

                for cmd, message_func in preset_messages.items():
                    if message.startswith(cmd):
                        _, *data = message.split(" ", maxsplit=1)
                        message = message_func(*data)
                print(f"> {message}")
                await websocket.send(message)


asyncio.get_event_loop().run_until_complete(hello())
