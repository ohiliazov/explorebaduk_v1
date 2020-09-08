import random
import asyncio

from explorebaduk.resources.player_list import player_online_payload, player_offline_payload
from tests.conftest import receive_messages, receive_all


async def test_login_first_player(test_cli, players_data: list):
    player_data = random.choice(players_data)
    player = player_data["player"]
    token = player_data["token"].token

    player_ws = await test_cli.ws_connect("/players/feed", headers={"Authorization": token})
    assert await player_ws.receive_json(timeout=0.5) == player.as_dict()


async def test_login_player(test_cli, players_data: list, players_online: dict):
    player_data = random.choice([player_data
                                 for player_data in players_data
                                 if player_data["player"] not in players_online.values()])
    player = player_data["player"]
    token = player_data["token"].token

    player_ws = await test_cli.ws_connect("/players/feed", headers={"Authorization": token})
    assert await player_ws.receive_json(timeout=0.5) == player.as_dict()

    for ws_messages in await receive_all(players_online):
        assert ws_messages[0] == player_online_payload(player)


async def test_logout_players(test_cli, players_data: list, players_online: dict):
    logout_ws = random.choice(list(players_online))
    player = players_online.pop(logout_ws)
    expected = player_offline_payload(player)

    await logout_ws.close()
    for ws in players_online:
        assert expected == await ws.receive_json()


async def test_refresh_player_list(test_cli, players_data: list):
    data = random.sample(players_data, 20)
    ws_list = await asyncio.gather(
        *[test_cli.ws_connect("/players/feed", headers={"Authorization": player_data["token"].token})
          for player_data in data]
    )

    expected = sorted([
        player_online_payload(player_data["player"]) for player_data in data],
        key=lambda item: item["player_id"]
    )

    await receive_all(ws_list)
    await asyncio.gather(*[ws.send_json({"action": "refresh"}) for ws in ws_list])

    for ws_messages in await receive_all(ws_list, sort_by=lambda item: item["player_id"]):
        assert ws_messages == expected
