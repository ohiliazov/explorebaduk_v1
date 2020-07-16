import random


async def test_get_user(test_cli):
    user_id = random.randint(0, 999)

    resp = await test_cli.get(f"/players/{user_id}")

    resp_json = await resp.json()
    assert resp_json["user_id"] == user_id
