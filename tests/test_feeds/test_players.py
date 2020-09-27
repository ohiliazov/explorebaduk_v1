import random
import asyncio
import simplejson as json

from explorebaduk.resources.player_list import player_online_payload, player_offline_payload
from tests.conftest import receive_messages, receive_all


def compare_message(actual, expected):
    assert actual == json.loads(json.dumps(expected))


async def test_login_first_player(test_cli, players_data: list):
    player_data = random.choice(players_data)
    player = player_data["player"]
    token = player_data["token"].token

    player_ws = await test_cli.ws_connect(
        test_cli.app.url_for("Players Feed"),
        headers={"Authorization": token},
    )

    actual = [msg for msg in await receive_messages(player_ws) if msg["status"] == "login"]
    compare_message(actual[0]["player"], player.as_dict())


async def test_login_player(test_cli, players_data: list, players_online: dict):
    player_data = random.choice([player_data
                                 for player_data in players_data
                                 if player_data["player"] not in players_online.values()])
    player = player_data["player"]
    token = player_data["token"].token

    player_ws = await test_cli.ws_connect(
        test_cli.app.url_for("Players Feed"),
        headers={"Authorization": token},
    )
    await receive_messages(player_ws)

    for ws_messages in await receive_all(players_online):
        compare_message(ws_messages[0], player_online_payload(player))


async def test_logout_players(test_cli, players_data: list, players_online: dict):
    logout_ws = random.choice(list(players_online))
    player = players_online.pop(logout_ws)
    expected = player_offline_payload(player)

    await logout_ws.close()
    for ws in players_online:
        assert expected == await ws.receive_json()


async def test_refresh_player_list(test_cli, players_data: list, players_online: dict):
    player_ws = random.choice(list(players_online))

    expected_messages = sorted(
        [
            player_online_payload(player)
            for player in players_online.values()
            if player is not players_online[player_ws]
        ],
        key=lambda item: item["player"]["player_id"]
    )

    await player_ws.send_json({"action": "refresh"})
    actual_messages = sorted(await receive_messages(player_ws), key=lambda item: item["player"]["player_id"])

    assert len(actual_messages) == len(expected_messages)
    for actual, expected in zip(actual_messages, expected_messages):
        compare_message(actual, expected)
