import random
import string

from asyncio import TimeoutError


async def receive_messages(ws):
    messages = []
    try:
        while True:
            messages.append(await ws.receive_json(timeout=0.5))
    except TimeoutError:
        pass

    return messages


async def test_login_player(test_cli):
    n = random.randint(2, 10)
    user_ids = random.sample(range(1, 101), n)

    tokens = [f"{string.ascii_letters}{user_id:012d}" for user_id in user_ids]

    ws_list = [await test_cli.ws_connect(f"/players_feed", headers={"Authorization": token}) for token in tokens]

    results = [sorted(await receive_messages(ws), key=lambda item: item["user_id"]) for ws in ws_list]
    assert all([results[0] == result for result in results])
