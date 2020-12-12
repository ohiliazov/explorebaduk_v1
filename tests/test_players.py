import asyncio
import random

import simplejson as json

from tests.conftest import receive_all, receive_messages


async def test_player_login_as_user(test_cli, users_data: list, players_online: dict):
    user_data = random.choice(
        [user_data for user_data in users_data if user_data not in players_online.values()],
    )
    user = user_data["user"]
    token = user_data["token"].token

    ws = await test_cli.ws_connect(test_cli.app.url_for("Players Feed"))

    await ws.send_json({"event": "authorize", "data": {"token": token}})

    expected = {"event": "players.whoami", "data": user.as_dict()}
    assert any([actual == json.loads(json.dumps(expected)) for actual in await receive_messages(ws)])

    for ws_messages in await receive_all(players_online):
        message = ws_messages[0]
        assert message["event"] == "players.add"
        assert message["data"]["user_id"] == user.user_id
        assert message["data"]["status"] == "online"


async def test_player_logout_as_user(test_cli, players_online: dict):
    logout_ws = random.choice(list(players_online))
    user = players_online.pop(logout_ws)["user"]

    await logout_ws.close()
    for ws_messages in await receive_all(players_online):
        message = ws_messages[0]
        assert message["event"] == "players.remove"
        assert message["data"] == {"user_id": user.user_id}


async def test_player_login_as_guest(test_cli, players_online: dict):

    player_ws = await test_cli.ws_connect(test_cli.app.url_for("Players Feed"))

    assert all(actual["event"] != "auth.login" for actual in await receive_messages(player_ws))


async def test_player_logout_as_guest(test_cli, players_online: dict):
    guest_ws = await test_cli.ws_connect(test_cli.app.url_for("Players Feed"))
    await guest_ws.close()

    for ws_messages in await receive_all(players_online):
        assert all([message["event"] != "players.remove" for message in ws_messages])


async def test_refresh_player_list(test_cli, players_online: dict):
    player_ws, user_data = random.choice(list(players_online.items()))

    await player_ws.send_json({"event": "refresh"})

    actual_messages = sorted(
        await receive_messages(player_ws),
        key=lambda item: item["data"]["user_id"],
    )
    expected_ids = sorted([user_data["user"].user_id for ws, user_data in players_online.items()])

    assert len(actual_messages) == len(expected_ids)
    for actual, expected_id in zip(actual_messages, expected_ids):
        assert actual["event"] == "players.add"
        assert actual["data"]["user_id"] == expected_id
        assert actual["data"]["status"] == "online"


async def test_player_multiple_login_as_user(test_cli, players_online: dict):
    user_data = random.choice(list(players_online.values()))
    token = user_data["token"].token

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
        assert all([message["event"] != "players.add" for message in ws_messages])


async def test_player_multiple_logout_as_user(test_cli, players_online: dict):
    player_ws, user_data = random.choice(list(players_online.items()))
    user = user_data["user"]
    token = user_data["token"].token

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

    event_message = {"event": "players.remove", "data": {"user_id": user.user_id}}
    for ws_messages in await receive_all(players_online):
        assert event_message not in ws_messages

    await player_ws.close()
    players_online.pop(player_ws)

    for ws_messages in await receive_all(players_online):
        assert event_message in ws_messages


async def test_player_multiple_login_as_guests(test_cli, players_online: dict):

    await asyncio.gather(*[test_cli.ws_connect(test_cli.app.url_for("Players Feed")) for _ in range(20)])

    not_expected = {"event": "players.add", "data": None}

    for ws_messages in await receive_all(players_online):
        assert not_expected not in ws_messages


async def test_player_multiple_logout_as_guest(test_cli, players_online: dict):

    guest_ws_list = await asyncio.gather(
        *[test_cli.ws_connect(test_cli.app.url_for("Players Feed")) for _ in range(20)]
    )
    await asyncio.gather(*[ws.close() for ws in guest_ws_list])

    not_expected = {"event": "players.remove", "data": {"user_id": None}}

    for ws_messages in await receive_all(players_online):
        assert not_expected not in ws_messages
