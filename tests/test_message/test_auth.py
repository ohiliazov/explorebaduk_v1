import random
import string

import pytest

from explorebaduk.message import parse_message, InvalidMessageError

good_username = "".join([random.choice(string.ascii_letters + string.digits) for _ in range(32)])
good_token = "".join([random.choice(string.ascii_letters + string.digits) for _ in range(64)])
bad_token = good_token


def test_auth_login_ok():
    for i in range(100):
        token = "".join([random.choice(string.ascii_letters + string.digits) for _ in range(64)])
        message_type, data = parse_message(f"auth login {token}")

        assert data == {"action": "login", "token": token}


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
