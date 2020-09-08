import random


async def test_get_user(test_cli, players_data: list):
    user_id = random.choice(players_data)["player"].user_id
    resp = await test_cli.get(f"/players/{user_id}")

    assert resp.status == 200

    resp_json = await resp.json()
    assert resp_json["user_id"] == user_id


async def test_get_absent_user(test_cli, players_data: list):
    user_id = 666

    resp = await test_cli.get(f"/players/{user_id}")

    assert resp.status == 404

    resp_json = await resp.json()
    assert resp_json["message"] == "User not found"
