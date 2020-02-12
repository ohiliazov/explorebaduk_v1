import pytest

CONNECTED_CLIENTS = 10


@pytest.mark.asyncio
async def test_test(start_test_server, client_factory):
    ws1 = await client_factory()
    await ws1.send("1234")
    print(await ws1.recv())
    print(await ws1.recv())
    print(await ws1.recv())
