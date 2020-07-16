import random
import asyncio

from asyncio import TimeoutError


async def receive_messages(ws, sort_by: callable = None):
    messages = []
    try:
        while True:
            messages.append(await ws.receive_json(timeout=0.5))
    except TimeoutError:
        pass

    if sort_by:
        messages = sorted(messages, key=sort_by)

    return messages


async def test_login_player(test_cli, users_data):
    tokens = [token for user_id, token in random.sample(users_data, 20)]
    ws_list = [await test_cli.ws_connect(f"/players_feed", headers={"Authorization": token}) for token in tokens]

    results = [await receive_messages(ws, lambda item: item["user_id"]) for ws in ws_list]
    assert all([results[0] == result for result in results])


async def test_logout_players(test_cli, users_data):
    tokens = [token for user_id, token in random.sample(users_data, 20)]
    ws_list = [await test_cli.ws_connect(f"/players_feed", headers={"Authorization": token}) for token in tokens]

    results = [await receive_messages(ws, lambda item: item["user_id"]) for ws in ws_list]
    assert all([results[0] == result for result in results])

    logout_ws = random.sample(ws_list, 10)
    await asyncio.gather(*[ws.close() for ws in logout_ws])

    results = [await receive_messages(ws, lambda item: item["user_id"]) for ws in ws_list if ws not in logout_ws]
    assert all([results[0] == result for result in results])


async def test_refresh_player_list(test_cli, users_data):
    tokens = [token for user_id, token in random.sample(users_data, 20)]
    ws_list = [await test_cli.ws_connect(f"/players_feed", headers={"Authorization": token}) for token in tokens]

    results = [await receive_messages(ws, lambda item: item["user_id"]) for ws in ws_list]
    assert all([results[0] == result for result in results])

    ws = random.choice(ws_list)
    await ws.send_str("refresh")

    result = await receive_messages(ws, lambda item: item["user_id"])
    assert len(result) == 20
