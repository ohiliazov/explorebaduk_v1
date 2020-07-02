import asyncio
import pytest
import random

from explorebaduk.database import UserModel, TokenModel
from explorebaduk.models import User

CONNECTED_CLIENTS = 10


def get_user(db, user_id):
    user = db.query(UserModel).filter_by(user_id=user_id).first()
    return user


def random_token(db, count: int = 1):
    user = random.sample(list(db.query(TokenModel).all()), count)
    return user


async def receive_messages(ws):
    responses = []
    try:
        while True:
            resp = await asyncio.wait_for(ws.recv(), timeout=0.5)
            responses.append(resp)

    except asyncio.TimeoutError:
        pass

    return responses


@pytest.mark.asyncio
async def test_auth_login_online_other_device(db_handler, ws_factory, game):
    ws1, ws2 = await ws_factory(2)

    token1, token2 = random_token(db_handler, 2)
    user1 = get_user(db_handler, token1.user_id)
    player1 = User(ws1, user1)
    user2 = get_user(db_handler, token2.user_id)
    player2 = User(ws2, user2)

    await ws1.send(f"auth login {token1.token}")
    await ws2.send(f"auth login {token2.token}")

    print(await receive_messages(ws1))
    print(await receive_messages(ws2))

    await ws1.send("challenge new GN[test]SZ[9:9]TS[1M3600O30P3S1B0]")
    print(await receive_messages(ws1))
    print(await receive_messages(ws2))

    await ws2.send(f"challenge join {player1.id}")
    print(await receive_messages(ws1))
    print(await receive_messages(ws2))

    await ws1.send(f"game start {player1.id} {player2.id}")
    messages = await receive_messages(ws1)

    black, white = ws1, ws2
    for message in messages:
        if message.startswith("game started"):
            if message.endswith(f"B[{player2.id}]W[{player1.id}]"):
                black, white = ws2, ws1

    print(await receive_messages(ws2))

    cursor = game.cursor()
    while not cursor.atEnd:
        node = cursor.next_node()

        move = node.get_prop("B") or node.get_prop("W")

        if move.label == "B":
            await black.send(f"game move 1 {move.values[0] if move.values else 'pass'}")
        else:
            await white.send(f"game move 1 {move.values[0] if move.values else 'pass'}")

        print(await receive_messages(ws1))
        print(await receive_messages(ws2))
