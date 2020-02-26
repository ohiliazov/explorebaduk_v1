import asyncio
import string
import websockets
import sys
import select


def auth_login(user_id: str = "1", *args):
    return f"auth login {string.ascii_letters}{int(user_id):012d}"


def challenge_cancel(challenge_id: str = "1", *args):
    return f"challenge cancel {challenge_id}"


def challenge_join(challenge_id: str = "1", *args):
    return f"challenge join {challenge_id}"


def challenge_leave(challenge_id: str = "1", *args):
    return f"challenge leave {challenge_id}"


def challenge_start(challenge_id: str = "1", opponent_id: str = "1", *args):
    return f"challenge start {challenge_id} {opponent_id}"


preset_messages = {
    "login": auth_login,
    "logout": lambda: "auth logout",
    "new": lambda: f"challenge new GN[Test]GI[0R0W19H19]FL[000]TS[0M3600O0P0S0B0D0]",
    "cancel": challenge_cancel,
    "join": challenge_join,
    "leave": challenge_leave,
    "start": challenge_start,
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
