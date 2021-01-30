import asyncio
import random

from explorebaduk.constants import EventName, RouteName
from explorebaduk.messages import (
    AuthorizeMessage,
    ErrorMessage,
    PlayersRemoveMessage,
    WhoAmIMessage,
)
from explorebaduk.utils.test_utils import receive_all, receive_messages


async def test_player_login_as_user(test_cli, users_data: list, players_online: dict):
    user_data = random.choice(
        [user_data for user_data in users_data if user_data not in players_online.values()],
    )
    user = user_data["user"]
    token = user_data["token"].token

    ws = await test_cli.ws_connect(test_cli.app.url_for(RouteName.PLAYERS_FEED))

    await ws.send_json(AuthorizeMessage(token).json())

    expected = WhoAmIMessage(user).json()
    assert any([actual == expected for actual in await receive_messages(ws)])

    for ws_messages in await receive_all(players_online):
        message = ws_messages[0]
        assert message["event"] == EventName.PLAYERS_ADD
        assert message["data"]["user_id"] == user.user_id
        assert message["data"]["status"] == "online"


async def test_player_logout_as_user(test_cli, players_online: dict):
    logout_ws = random.choice(list(players_online))
    user = players_online.pop(logout_ws)["user"]

    await logout_ws.close()

    expected = PlayersRemoveMessage(user).json()
    for ws_messages in await receive_all(players_online):
        assert expected in ws_messages


async def test_player_login_as_guest(test_cli, players_online: dict):
    ws = await test_cli.ws_connect(test_cli.app.url_for(RouteName.PLAYERS_FEED))

    await ws.send_json(AuthorizeMessage().json())

    not_expected = WhoAmIMessage(None).json()
    assert not_expected not in await receive_messages(ws)

    for ws_messages in await receive_all(players_online):
        assert not ws_messages


async def test_player_login_invalid_token(test_cli, players_online: dict):
    player_ws = await test_cli.ws_connect(test_cli.app.url_for(RouteName.PLAYERS_FEED))
    await receive_messages(player_ws)

    await player_ws.send_json(AuthorizeMessage("invalid_token").json())

    expected = ErrorMessage("Invalid or expired token provided").json()
    assert expected in await receive_messages(player_ws)

    for ws_messages in await receive_all(players_online):
        assert not ws_messages


async def test_player_login_expired_token(test_cli, users_data: list, players_online: dict):
    user_data = random.choice(users_data)
    player_ws = await test_cli.ws_connect(test_cli.app.url_for(RouteName.PLAYERS_FEED))
    await receive_messages(player_ws)

    await player_ws.send_json(AuthorizeMessage(user_data["expired_token"].token).json())

    expected = ErrorMessage("Invalid or expired token provided").json()
    assert expected in await receive_messages(player_ws)

    for ws_messages in await receive_all(players_online):
        assert not ws_messages


async def test_player_logout_as_guest(test_cli, players_online: dict):
    guest_ws = await test_cli.ws_connect(test_cli.app.url_for(RouteName.PLAYERS_FEED))
    await guest_ws.send_json(AuthorizeMessage().json())
    await receive_messages(guest_ws)
    await guest_ws.close()

    expected = PlayersRemoveMessage(None).json()

    for ws_messages in await receive_all(players_online):
        assert expected not in ws_messages


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
        assert actual["data"]["status"] == "online"
        assert actual["event"] == EventName.PLAYERS_ADD
        assert actual["data"]["user_id"] == expected_id


async def test_player_multiple_login_as_user(test_cli, players_online: dict):
    user_data = random.choice(list(players_online.values()))
    token = user_data["token"].token

    ws_list = await asyncio.gather(
        *[test_cli.ws_connect(test_cli.app.url_for(RouteName.PLAYERS_FEED)) for _ in range(20)]
    )
    await asyncio.gather(*[ws.send_json(AuthorizeMessage(token).json()) for ws in ws_list])

    for ws_messages in await receive_all(players_online):
        assert not ws_messages


async def test_player_multiple_login_as_guests(test_cli, players_online: dict):

    ws_list = await asyncio.gather(
        *[test_cli.ws_connect(test_cli.app.url_for(RouteName.PLAYERS_FEED)) for _ in range(20)]
    )
    await asyncio.gather(*[ws.send_json(AuthorizeMessage().json()) for ws in ws_list])

    for ws_messages in await receive_all(players_online):
        assert not ws_messages
