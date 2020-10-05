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
    user_id = user_data["user"].user_id

    await ws.send_json({"action": "set", "challenge": {"dummy": "dummy"}})

    expected = {"status": "active", "user_id": user_id, "challenge": {"dummy": "dummy"}}
    for ws_messages in await receive_all(set(challenges_online) - {ws}):
        assert expected in ws_messages


async def test_challenge_set_twice(test_cli, challenges_online: dict):
    ws, user_data = random.choice(list(challenges_online.items()))
    challenge_data = {"dummy": "dummy"}
    user_id = user_data["user"].user_id
    await ws.send_json({"action": "set", "challenge": challenge_data})

    expected = {"status": "active", "user_id": user_id, "challenge": challenge_data}
    for ws_messages in await receive_all(set(challenges_online) - {ws}):
        assert expected in ws_messages

    challenge_data = {"dummy": "dummy2"}
    await ws.send_json({"action": "set", "challenge": challenge_data})

    expected = {"status": "active", "user_id": user_id, "challenge": challenge_data}
    for ws_messages in await receive_all(set(challenges_online) - {ws}):
        assert expected in ws_messages


async def test_challenge_unset(test_cli, challenges_online: dict):
    ws, user_data = random.choice(list(challenges_online.items()))
    challenge_data = {"dummy": "dummy"}
    user_id = user_data["user"].user_id
    await ws.send_json({"action": "set", "challenge": challenge_data})
    await receive_all(challenges_online)

    await ws.send_json({"action": "unset"})
    expected = {"status": "inactive", "user_id": user_id, "challenge": None}
    for ws_messages in await receive_all(set(challenges_online) - {ws}):
        assert expected in ws_messages
