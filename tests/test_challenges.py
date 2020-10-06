import random
import simplejson as json

from explorebaduk.constants import ALLOWED_TIME_SYSTEMS
from tests.conftest import receive_messages, receive_all


def compare_message(actual, expected):
    assert actual == json.loads(json.dumps(expected))


def generate_time_settings(time_system):
    if time_system == "absolute":
        return {"main_time": 3600}
    if time_system == "japanese":
        return {"main_time": 3600, "overtime": 300, "periods": 5}
    if time_system == "canadian":
        return {"main_time": 3600, "overtime": 300, "stones": 20}
    if time_system == "fischer":
        return {"main_time": 3600, "bonus": 10}
    return {}


def generate_challenge_data():
    time_system = random.choice(ALLOWED_TIME_SYSTEMS)
    return {
        "game_setup": {
            "name": f"Game name #{random.randint(0, 10000)}",
            "type": "ranked",
        },
        "rule_set": {
            "rules": "japanese",
            "board_size": 19,
        },
        "time_settings": {
            "time_system": time_system,
            **generate_time_settings(time_system),
        },
    }


def generate_expected_data(challenge_data: dict):
    expected_data = {k: v.copy() for k, v in challenge_data.items()}
    expected_data["game_setup"].setdefault("is_private", False)
    expected_data["rule_set"].setdefault("board_size", 19)
    expected_data["time_settings"].setdefault("main_time", 0)
    expected_data["time_settings"].setdefault("overtime", 0)
    expected_data["time_settings"].setdefault("periods", 1)
    expected_data["time_settings"].setdefault("stones", 1)
    expected_data["time_settings"].setdefault("bonus", 0)
    return expected_data


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
    challenge_data = generate_challenge_data()
    expected_data = generate_expected_data(challenge_data)
    expected = {"status": "active", "user_id": user_id, "challenge": expected_data}

    await ws.send_json({"action": "set", "challenge": challenge_data})

    messages = await receive_messages(ws)
    assert {"action": "set", "data": expected_data, "errors": {}} in messages

    for ws_messages in await receive_all(set(challenges_online) - {ws}):
        assert expected in ws_messages


async def test_challenge_set_twice(test_cli, challenges_online: dict):
    ws, user_data = random.choice(list(challenges_online.items()))

    await ws.send_json({"action": "set", "challenge": generate_challenge_data()})
    await receive_all(challenges_online)

    user_id = user_data["user"].user_id
    challenge_data = generate_challenge_data()
    expected_data = generate_expected_data(challenge_data)

    await ws.send_json({"action": "set", "challenge": challenge_data})

    messages = await receive_messages(ws)
    assert {"action": "set", "data": expected_data, "errors": {}} in messages

    expected = {"status": "active", "user_id": user_id, "challenge": expected_data}
    for ws_messages in await receive_all(set(challenges_online) - {ws}):
        assert expected in ws_messages


async def test_challenge_set_unset_set(test_cli, challenges_online: dict):
    ws, user_data = random.choice(list(challenges_online.items()))

    await ws.send_json({"action": "set", "challenge": generate_challenge_data()})
    await receive_all(challenges_online)

    await ws.send_json({"action": "unset"})
    await receive_all(challenges_online)

    user_id = user_data["user"].user_id
    challenge_data = generate_challenge_data()
    expected_data = generate_expected_data(challenge_data)

    await ws.send_json({"action": "set", "challenge": challenge_data})

    messages = await receive_messages(ws)
    assert {"action": "set", "data": expected_data, "errors": {}} in messages

    expected = {"status": "active", "user_id": user_id, "challenge": expected_data}
    for ws_messages in await receive_all(set(challenges_online) - {ws}):
        assert expected in ws_messages


async def test_challenge_unset(test_cli, challenges_online: dict):
    ws, user_data = random.choice(list(challenges_online.items()))

    await ws.send_json({"action": "set", "challenge": generate_challenge_data()})
    await receive_all(challenges_online)

    user_id = user_data["user"].user_id

    await ws.send_json({"action": "unset"})

    messages = await receive_messages(ws)
    assert {"action": "unset", "data": None} in messages

    expected = {"status": "inactive", "user_id": user_id, "challenge": None}
    for ws_messages in await receive_all(set(challenges_online) - {ws}):
        assert expected in ws_messages


async def test_challenge_unset_twice(test_cli, challenges_online: dict):
    ws, user_data = random.choice(list(challenges_online.items()))

    await ws.send_json({"action": "set", "challenge": generate_challenge_data()})
    await receive_all(challenges_online)

    await ws.send_json({"action": "unset"})
    await receive_all(challenges_online)

    user_id = user_data["user"].user_id
    not_expected = {"status": "inactive", "user_id": user_id, "challenge": None}

    await ws.send_json({"action": "unset"})

    messages = await receive_messages(ws)
    assert {"action": "unset", "data": None} in messages

    for ws_messages in await receive_all(set(challenges_online) - {ws}):
        assert not_expected not in ws_messages


async def test_challenge_unset_inactive(test_cli, challenges_online: dict):
    ws, user_data = random.choice(list(challenges_online.items()))
    user_id = user_data["user"].user_id

    await ws.send_json({"action": "unset"})

    messages = await receive_messages(ws)
    assert {"action": "unset", "data": None} in messages

    not_expected = {"status": "inactive", "user_id": user_id, "challenge": None}
    for ws_messages in await receive_all(set(challenges_online) - {ws}):
        assert not_expected not in ws_messages
