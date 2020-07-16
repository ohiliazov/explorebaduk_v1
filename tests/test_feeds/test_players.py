import random
import string
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


async def test_login_player(test_cli):
    n = random.randint(2, 50)
    user_ids = random.sample(range(1, 101), n)

    tokens = [f"{string.ascii_letters}{user_id:012d}" for user_id in user_ids]

    ws_list = [await test_cli.ws_connect(f"/players_feed", headers={"Authorization": token}) for token in tokens]

    results = [await receive_messages(ws, lambda item: item["user_id"]) for ws in ws_list]
    assert all([results[0] == result for result in results])


async def test_logout_players(test_cli):
    n = random.randint(2, 50)
    user_ids = random.sample(range(1, 101), n)

    m = random.randint(1, n-1)
    tokens = [f"{string.ascii_letters}{user_id:012d}" for user_id in user_ids]

    ws_list = [await test_cli.ws_connect(f"/players_feed", headers={"Authorization": token}) for token in tokens]

    results = [await receive_messages(ws, lambda item: item["user_id"]) for ws in ws_list]
    assert all([results[0] == result for result in results])

    logout_ws = random.sample(ws_list, m)
    await asyncio.gather(*[ws.close() for ws in logout_ws])

    results = [await receive_messages(ws, lambda item: item["user_id"]) for ws in ws_list if ws not in logout_ws]
    assert all([results[0] == result for result in results])
