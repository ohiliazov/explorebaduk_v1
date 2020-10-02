import asyncio
import random
import simplejson as json

from tests.conftest import receive_messages, receive_all


def compare_message(actual, expected):
    assert actual == json.loads(json.dumps(expected))


async def test_login_player(test_cli, users_data: list):
    user_data = random.choice(users_data)
    user = user_data["user"]
    token = user_data["token"].token

    ws = await test_cli.ws_connect(
        test_cli.app.url_for("Players Feed"),
        headers={"Authorization": token},
    )

    expected = {"status": "login", "player": user.as_dict()}
    assert any(
        actual == json.loads(json.dumps(expected))
        for actual in await receive_messages(ws)
    )


async def test_login_player_online_message(
    test_cli, users_data: list, players_online: dict
):
    user_data = random.choice(
        [
            user_data
            for user_data in users_data
            if user_data not in players_online.values()
        ],
    )
    user = user_data["user"]
    token = user_data["token"].token

    expected = {"status": "online", "player": user.as_dict()}

    player_ws = await test_cli.ws_connect(
        test_cli.app.url_for("Players Feed"),
        headers={"Authorization": token},
    )
    await receive_messages(player_ws)

    for ws_messages in await receive_all(players_online):
        compare_message(ws_messages[0], expected)


async def test_logout_players_offline_message(test_cli, players_online: dict):
    logout_ws = random.choice(list(players_online))
    user = players_online.pop(logout_ws)["user"]
    expected = {"status": "offline", "player": user.as_dict()}

    await logout_ws.close()
    for ws in players_online:
        compare_message(await ws.receive_json(), expected)


async def test_refresh_player_list(test_cli, players_online: dict):
    player_ws = random.choice(list(players_online))

    expected_messages = sorted(
        [
            {"status": "online", "player": user_data["user"].as_dict()}
            for ws, user_data in players_online.items()
            if ws is not player_ws
        ],
        key=lambda item: item["player"]["user_id"],
    )

    await player_ws.send_json({"action": "refresh"})
    actual_messages = sorted(
        await receive_messages(player_ws),
        key=lambda item: item["player"]["user_id"],
    )

    assert len(actual_messages) == len(expected_messages)
    for actual, expected in zip(actual_messages, expected_messages):
        compare_message(actual, expected)


async def test_login_player_multiple_devices(test_cli, players_online: dict):
    _, user_data = random.choice(list(players_online.items()))
    user = user_data["user"]
    token = user_data["token"].token

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


async def test_logout_player_multiple_devices(test_cli, players_online: dict):
    player_ws, user_data = random.choice(list(players_online.items()))
    user = user_data["user"]
    token = user_data["token"].token

    not_expected = {"status": "offline", "player": user.as_dict()}

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


async def test_login_guest(test_cli, players_online: dict):

    player_ws = await test_cli.ws_connect(test_cli.app.url_for("Players Feed"))

    expected = {"status": "login", "player": None}
    assert any(
        actual == json.loads(json.dumps(expected))
        for actual in await receive_messages(player_ws)
    )


async def test_login_multiple_guests(test_cli, players_online: dict):

    await asyncio.gather(
        *[test_cli.ws_connect(test_cli.app.url_for("Players Feed")) for _ in range(20)]
    )

    not_expected = {"status": "online", "player": None}

    for ws_messages in await receive_all(players_online):
        assert not_expected not in ws_messages


async def test_logout_guest(test_cli, players_online: dict):
    guest_ws = await test_cli.ws_connect(test_cli.app.url_for("Players Feed"))
    await guest_ws.close()
    not_expected = {"status": "offline", "player": None}

    for ws_messages in await receive_all(players_online):
        assert not_expected not in ws_messages


async def test_logout_multiple_guests(test_cli, players_online: dict):

    guest_ws_list = await asyncio.gather(
        *[test_cli.ws_connect(test_cli.app.url_for("Players Feed")) for _ in range(20)]
    )
    await asyncio.gather(*[ws.close() for ws in guest_ws_list])

    not_expected = {"status": "offline", "player": None}

    for ws_messages in await receive_all(players_online):
        assert not_expected not in ws_messages
