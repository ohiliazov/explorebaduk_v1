import random


async def test_get_player(test_cli):
    player_id = random.randint(0, 999)

    resp = await test_cli.get(f"/players/{player_id}")

    resp_json = await resp.json()
    assert resp_json == {"player_id": str(player_id)}
