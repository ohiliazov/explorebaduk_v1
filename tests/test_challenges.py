import random

from tests.conftest import receive_all


async def test_challenges_create(test_cli, challenges_online: dict):
    user_data = random.choice(list(challenges_online.values()))
    challenge_data = {
        "game_setup": {
            "name": "Game 1",
            "type": "ranked",
        },
        "rule_set": {
            "rules": "japanese",
        },
        "time_settings": {
            "time_system": "absolute",
            "main_time": 3600,
        },
    }

    resp = await test_cli.post(
        test_cli.app.url_for("Challenges View"),
        json=challenge_data,
        headers={"Authorization": user_data["token"].token},
    )

    assert resp.status == 201

    event_message = {
        "event": "challenges.add",
        "data": {
            "user_id": user_data["user"].user_id,
            "game_setup": {"name": "Game 1", "type": "ranked", "is_private": False},
            "rule_set": {"rules": "japanese", "board_size": 19},
            "time_settings": {
                "time_system": "absolute",
                "main_time": 3600,
                "overtime": 0,
                "periods": 1,
                "stones": 1,
                "bonus": 0,
            },
        },
    }
    for ws_messages in await receive_all(challenges_online):
        assert event_message in ws_messages


async def test_challenges_update(test_cli, challenges_online: dict):
    user_data = random.choice(list(challenges_online.values()))
    challenge_data = {
        "game_setup": {
            "name": "Game 1",
            "type": "ranked",
        },
        "rule_set": {
            "rules": "japanese",
        },
        "time_settings": {
            "time_system": "absolute",
            "main_time": 3600,
        },
    }

    await test_cli.post(
        test_cli.app.url_for("Challenges View"),
        json=challenge_data,
        headers={"Authorization": user_data["token"].token},
    )
    await receive_all(challenges_online)

    challenge_data["game_setup"]["name"] = "Game 2"
    resp = await test_cli.post(
        test_cli.app.url_for("Challenges View"),
        json=challenge_data,
        headers={"Authorization": user_data["token"].token},
    )
    assert resp.status == 201

    event_message = {
        "event": "challenges.update",
        "data": {
            "user_id": user_data["user"].user_id,
            "game_setup": {"name": "Game 2", "type": "ranked", "is_private": False},
            "rule_set": {"rules": "japanese", "board_size": 19},
            "time_settings": {
                "time_system": "absolute",
                "main_time": 3600,
                "overtime": 0,
                "periods": 1,
                "stones": 1,
                "bonus": 0,
            },
        },
    }
    for ws_messages in await receive_all(challenges_online):
        assert event_message in ws_messages
