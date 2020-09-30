import asyncio
import random
import simplejson as json

from tests.conftest import receive_messages, receive_all


def compare_message(actual, expected):
    assert actual == json.loads(json.dumps(expected))


async def test_login_player(test_cli, players_data: list):
    player_data = random.choice(players_data)
    user = player_data["user"]
    token = player_data["token"].token

    player_ws = await test_cli.ws_connect(
        test_cli.app.url_for("Players Feed"),
        headers={"Authorization": token},
    )

    expected = {"status": "login", "player": user.as_dict()}
    assert any(actual == json.loads(json.dumps(expected)) for actual in await receive_messages(player_ws))


async def test_login_player_online_message(test_cli, players_data: list, players_online: dict):
    player_data = random.choice(
        [player_data for player_data in players_data if player_data not in players_online.values()],
    )
    user = player_data["user"]
    token = player_data["token"].token

    expected = {"status": "online", "player": user.as_dict()}

    player_ws = await test_cli.ws_connect(
        test_cli.app.url_for("Players Feed"),
        headers={"Authorization": token},
    )
    await receive_messages(player_ws)

    for ws_messages in await receive_all(players_online):
        compare_message(ws_messages[0], expected)


async def test_logout_players_offline_message(test_cli, players_data: list, players_online: dict):
    logout_ws = random.choice(list(players_online))
    user = players_online.pop(logout_ws)["user"]
    expected = {"status": "offline", "player": user.as_dict()}

    await logout_ws.close()
    for ws in players_online:
        compare_message(await ws.receive_json(), expected)


async def test_refresh_player_list(test_cli, players_data: list, players_online: dict):
    player_ws = random.choice(list(players_online))

    expected_messages = sorted(
        [
            {"status": "online", "player": player_data["user"].as_dict()}
            for ws, player_data in players_online.items()
            if ws is not player_ws
        ],
        key=lambda item: item["player"]["user_id"],
    )

    await player_ws.send_json({"action": "refresh"})
    actual_messages = sorted(await receive_messages(player_ws), key=lambda item: item["player"]["user_id"])

    assert len(actual_messages) == len(expected_messages)
    for actual, expected in zip(actual_messages, expected_messages):
        compare_message(actual, expected)


async def test_login_player_no_message_multiple_devices(test_cli, players_data: list, players_online: dict):
    _, player_data = random.choice(list(players_online.items()))
    user = player_data["user"]
    token = player_data["token"].token

    not_expected = {"status": "online", "player": user.as_dict()}

    await asyncio.gather(
        *[
            test_cli.ws_connect(
                test_cli.app.url_for("Players Feed"),
                headers={"Authorization": token},
            )
            for _ in range(20)
        ]
    )

    for ws_messages in await receive_all(players_online):
        assert not_expected not in ws_messages


async def test_logout_player_no_message_multiple_devices(test_cli, players_data: list, players_online: dict):
    player_ws, player_data = random.choice(list(players_online.items()))
    user = player_data["user"]
    token = player_data["token"].token

    not_expected = {"status": "ofline", "player": user.as_dict()}

    player_ws_list = await asyncio.gather(
        *[
            test_cli.ws_connect(
                test_cli.app.url_for("Players Feed"),
                headers={"Authorization": token},
            )
            for _ in range(20)
        ]
    )

    await receive_all(players_online)

    await asyncio.gather(*[ws.close() for ws in player_ws_list])

    for ws_messages in await receive_all(players_online):
        assert not_expected not in ws_messages
