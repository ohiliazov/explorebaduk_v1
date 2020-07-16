import pytest
import random
import string
import uuid


@pytest.fixture
async def challenges(test_cli):
    challenge_ids = []
    for i in range(10):
        token = factory_token()
        resp = await test_cli.post(
            "/challenges",
            headers={"Authorization": token},
            json=factory_challenge_payload(with_time_settings=(i % 2 == 0), with_opponent=(i % 3 == 0)),
        )
        assert resp.status == 200

        resp_json = await resp.json()
        challenge_id = resp_json["challenge_id"]
        challenge_ids.append((token, challenge_id))

    return challenge_ids


def make_token(user_id: int):
    return f"{string.ascii_letters}{user_id:012d}"


def factory_token():
    return make_token(random.randint(1, 100))


def factory_challenge_payload(with_time_settings: bool = False, with_opponent: bool = False):
    payload = {
        "game_setup": {"name": "Test Name", "type": random.choice(["ranked", "free"]), "opponent_id": None,},
        "rule_set": {
            "rules": random.choice(["japanese", "chinese"]),
            "board_size": random.randint(5, 52),
            "handicap": None,
            "komi": None,
        },
        "time_settings": {"time_system": random.choice(["unlimited", "absolute", "byo-yomi", "canadian", "fischer"]),},
    }

    if with_time_settings:
        payload["time_settings"] = {
            "time_system": "absolute",
            "main_time": random.choice([0, 600, 3600]),
        }

    if with_opponent:
        payload["game_setup"]["opponent_id"] = random.randint(1, 100)
        payload["rule_set"]["handicap"] = random.choice([0, 2, 3, 4, 5, 6, 7, 8, 9])
        payload["rule_set"]["komi"] = random.randint(-6, 6) + random.choice([0, 0.5])

    return payload


async def test_create_challenge(test_cli):
    resp = await test_cli.post(
        "/challenges",
        headers={"Authorization": factory_token()},
        json=factory_challenge_payload(),
    )
    assert resp.status == 200

    resp_json = await resp.json()
    assert resp_json["message"] == "Challenge created"


async def test_create_challenge_with_time_settings(test_cli):
    resp = await test_cli.post(
        "/challenges",
        headers={"Authorization": factory_token()},
        json=factory_challenge_payload(with_time_settings=True),
    )
    assert resp.status == 200

    resp_json = await resp.json()
    assert resp_json["message"] == "Challenge created"


async def test_create_challenge_with_opponent(test_cli):
    resp = await test_cli.post(
        "/challenges",
        headers={"Authorization": factory_token()},
        json=factory_challenge_payload(with_time_settings=True, with_opponent=True),
    )
    assert resp.status == 200

    resp_json = await resp.json()
    assert resp_json["message"] == "Challenge created"


async def test_create_challenge_no_user(test_cli):
    resp = await test_cli.post(
        "/challenges",
        json=factory_challenge_payload(),
    )

    assert resp.status == 403

    resp_json = await resp.json()
    assert resp_json["message"] == "Forbidden to create challenge"


async def test_update_challenge(test_cli, challenges):
    token, challenge_id = random.choice(challenges)
    resp = await test_cli.put(
        f"/challenges/{challenge_id}",
        headers={"Authorization": token},
        json=factory_challenge_payload(),
    )
    assert resp.status == 200

    resp_json = await resp.json()
    assert resp_json["message"] == "Challenge updated"


async def test_update_absent_challenge(test_cli, challenges):
    resp = await test_cli.put(
        f"/challenges/{str(uuid.uuid4())}",
        headers={"Authorization": factory_token()},
        json=factory_challenge_payload(),
    )

    assert resp.status == 404

    resp_json = await resp.json()
    assert resp_json["message"] == "Challenge not found"


async def test_update_challenge_no_user(test_cli, challenges):
    _, challenge_id = random.choice(challenges)
    resp = await test_cli.put(
        f"/challenges/{challenge_id}",
        json=factory_challenge_payload(),
    )

    assert resp.status == 403

    resp_json = await resp.json()
    assert resp_json["message"] == "Forbidden to update challenge"


async def test_update_challenge_wrong_user(test_cli, challenges):
    token, challenge_id = random.choice(challenges)

    while (wrong_token := factory_token()) == token:
        pass

    resp = await test_cli.put(
        f"/challenges/{challenge_id}",
        headers={"Authorization": wrong_token},
        json=factory_challenge_payload(),
    )

    assert resp.status == 403

    resp_json = await resp.json()
    assert resp_json["message"] == "Forbidden to update challenge"
