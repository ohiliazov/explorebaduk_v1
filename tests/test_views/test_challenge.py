import random
import string


def factory_token():
    user_id = random.randint(1, 100)
    return f"{string.ascii_letters}{user_id:012d}"


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


async def test_post_challenge(test_cli):
    payload = factory_challenge_payload()

    resp = await test_cli.post("/challenges", json=payload, headers={"Authorization": factory_token()})

    assert resp.status == 200

    resp_json = await resp.json()
    assert resp_json["message"] == "Challenge created"


async def test_post_challenge_with_time_settings(test_cli):
    payload = factory_challenge_payload(with_time_settings=True)

    resp = await test_cli.post("/challenges", json=payload, headers={"Authorization": factory_token()})

    assert resp.status == 200

    resp_json = await resp.json()
    assert resp_json["message"] == "Challenge created"


async def test_post_challenge_with_opponent(test_cli):
    payload = factory_challenge_payload(with_time_settings=True, with_opponent=True)

    resp = await test_cli.post("/challenges", json=payload, headers={"Authorization": factory_token()})

    assert resp.status == 200

    resp_json = await resp.json()
    assert resp_json["message"] == "Challenge created"


async def test_post_challenge_no_user(test_cli):
    payload = factory_challenge_payload()

    resp = await test_cli.post("/challenges", json=payload)

    assert resp.status == 403

    resp_json = await resp.json()
    assert resp_json["message"] == "Forbidden to create challenge"
