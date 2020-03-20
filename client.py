import asyncio
import random
import string
import websockets
import sys
import select

from config import SERVER_HOST, SERVER_PORT

BOARD_SIZE_CHOICES = ["19:19", "13:13", "9:9"]
# FLAGS_CHOICES = ["000", "001", "010", "011", "100", "101", "110", "111"]
TIME_CONTROL_CHOICES = [
    f"0",
    f"1M{random.randint(60, 3600)}",
    f"2M{random.randint(60, 3600)}O60P5",
    f"3M{random.randint(60, 3600)}O600S15",
    f"4M{random.randint(60, 3600)}B7",
]


def auth_login(user_id: str = "1", *args):
    return f"auth login {string.ascii_letters}{int(user_id):012d}"


def challenge_cancel(challenge_id: str = "1", *args):
    return f"challenge cancel {challenge_id}"


def challenge_join(challenge_id: str = "1", *args):
    return f"challenge join {challenge_id}"


def challenge_leave(challenge_id: str = "1", *args):
    return f"challenge leave {challenge_id}"


def game_start(challenge_id: str = "1", opponent_id: str = "1", *args):
    return f"game start {challenge_id} {opponent_id}"


def challenge_new():
    game_name = "Test Game Request"
    board_size = random.choice(BOARD_SIZE_CHOICES)
    # flags = random.choice(FLAGS_CHOICES)
    time_control = random.choice(TIME_CONTROL_CHOICES)

    return (
        f"challenge new GN[{game_name}]"
        f"SZ[{board_size}]"
        # f"FL[{flags}]"
        f"TS[{time_control}]"
    )


preset_messages = {
    "login": auth_login,
    "logout": lambda: "auth logout",
    "new": challenge_new,
    "cancel": challenge_cancel,
    "join": challenge_join,
    "leave": challenge_leave,
    "start": game_start,
}


async def hello():
    uri = f"ws://{SERVER_HOST}:{SERVER_PORT}"
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
