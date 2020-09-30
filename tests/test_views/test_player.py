import random


async def test_get_user(test_cli, players_data: list):
    user = random.choice(players_data)["user"]
    resp = await test_cli.get(f"/players/{user.user_id}")

    assert resp.status == 200

    resp_json = await resp.json()
    assert resp_json == user.as_dict()


async def test_get_absent_user(test_cli, players_data: list):
    resp = await test_cli.get("/players/666")
    assert resp.status == 404
