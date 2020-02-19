import asyncio
import websockets
import pytest

from config import TEST_SERVER_HOST, TEST_SERVER_PORT
from app import start_server


@pytest.fixture
def event_loop():
    return asyncio.get_event_loop()


@pytest.yield_fixture(autouse=True)
async def start_test_server(event_loop):
    server = await websockets.serve(start_server, TEST_SERVER_HOST, TEST_SERVER_PORT, loop=event_loop)
    yield
    server.close()


@pytest.yield_fixture
async def ws1(event_loop):
    ws = await websockets.connect(f'ws://{TEST_SERVER_HOST}:{TEST_SERVER_PORT}', loop=event_loop)
    yield ws
    await ws.close()

@pytest.yield_fixture
async def ws2(event_loop):
    ws = await websockets.connect(f'ws://{TEST_SERVER_HOST}:{TEST_SERVER_PORT}', loop=event_loop)
    yield ws
    await ws.close()
