import random
import string

import pytest

from explorebaduk.message import parse_message, InvalidMessageError

good_username = "".join(
    [random.choice(string.ascii_letters + string.digits) for _ in range(32)]
)
good_token = "".join(
    [random.choice(string.ascii_letters + string.digits) for _ in range(64)]
)
bad_token = good_token


def test_auth_login_ok():
    for i in range(100):
        user_id = "".join([random.choice(string.digits) for _ in range(i + 1)])
        token = "".join(
            [random.choice(string.ascii_letters + string.digits) for _ in range(64)]
        )
        message_type, data = parse_message(f"auth login {user_id} {token}")

        assert data == {"action": "login", "user_id": user_id, "token": token}


@pytest.mark.parametrize(
    "message",
    [
        f"auth login {good_username} {good_token[:-1]}",
        f"auth login {good_username} {good_token} ",
        f"auth login {good_username} {good_token}z",
        f"auth login {good_username} ",
        f"auth login {good_username}",
        f"auth login ",
        f"auth login",
    ],
)
def test_auth_login_error(message):
    with pytest.raises(InvalidMessageError):
        parse_message(message)


@pytest.mark.parametrize(
    "message, expected",
    [
        [
            "challenge new GT0RL0PL2 19:19 F000 T0M3600O0P0S0B0D0 My Challenge",
            {
                "action": "new",
                "game_type": "0",
                "name": "My Challenge",
                "rules": "0",
                "players_num": "2",
                "width": "19",
                "height": "19",
                "is_open": "0",
                "undo": "0",
                "pause": "0",
                "time_system": "0",
                "main_time": "3600",
                "overtime": "0",
                "periods": "0",
                "stones": "0",
                "bonus": "0",
                "delay": "0",
            },
        ],
        [
            "challenge new GT0RL1PL2 9:9 F000 T1M3600O30P5S1B0D0 Let's play 9x9",
            {
                "action": "new",
                "game_type": "0",
                "name": "Let's play 9x9",
                "rules": "1",
                "players_num": "2",
                "width": "9",
                "height": "9",
                "is_open": "0",
                "undo": "0",
                "pause": "0",
                "time_system": "1",
                "main_time": "3600",
                "overtime": "30",
                "periods": "5",
                "stones": "1",
                "bonus": "0",
                "delay": "0",
            },
        ],
        [
            "challenge new GT0RL3PL2 19:19 F101 T1M3600O30P5S1B0D0 abcEFG",
            {
                "action": "new",
                "game_type": "0",
                "name": "abcEFG",
                "rules": "3",
                "players_num": "2",
                "width": "19",
                "height": "19",
                "is_open": "1",
                "undo": "0",
                "pause": "1",
                "time_system": "1",
                "main_time": "3600",
                "overtime": "30",
                "periods": "5",
                "stones": "1",
                "bonus": "0",
                "delay": "0",
            },
        ],
    ],
)
def test_challenge_new_ok(message, expected):
    message_type, data = parse_message(message)
    assert data == expected
