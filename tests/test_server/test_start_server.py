import pytest


CONNECTED_CLIENTS = 10


def login_message(token):
    return f"auth login {token.token}"


@pytest.mark.asyncio
async def test_auth_login(client_factory, user1, token1):
    ws1 = await client_factory()
    await ws1.send(login_message(token1))
    print(await ws1.recv())
    print(await ws1.recv())
    print(await ws1.recv())
