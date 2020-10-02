import random
import simplejson as json

from tests.conftest import receive_messages, receive_all


def compare_message(actual, expected):
    assert actual == json.loads(json.dumps(expected))


async def test_challenge_connect_as_user(test_cli, users_data: list):
    user_data = random.choice(users_data)

    user = user_data["user"]

    ws = await test_cli.ws_connect(
        test_cli.app.url_for("Challenges Feed"),
        headers={"Authorization": user_data["token"].token},
    )

    expected = {"status": "login", "user": user.as_dict()}
    assert any(
        actual == json.loads(json.dumps(expected))
        for actual in await receive_messages(ws)
    )


async def test_challenge_connect_as_guest(test_cli, users_data: list):
    ws = await test_cli.ws_connect(test_cli.app.url_for("Challenges Feed"))

    expected = {"status": "login", "user": None}
    assert any(
        actual == json.loads(json.dumps(expected))
        for actual in await receive_messages(ws)
    )


async def test_challenge_set(test_cli, challenges_online: dict):
    ws, user_data = random.choice(list(challenges_online.items()))

    await ws.send_json({"action": "set", "challenge": {"dummy": "dummy"}})

    expected = {"status": "active", "challenge": {"dummy": "dummy"}}
    for ws_messages in await receive_all(set(challenges_online) - {ws}):
        assert expected in ws_messages
