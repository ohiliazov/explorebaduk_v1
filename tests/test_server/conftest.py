import asyncio
import websockets
import pytest
from sqlalchemy import create_engine

from config import TEST_DATABASE_URI, TEST_SERVER_HOST, TEST_SERVER_PORT
from app import start_server


@pytest.fixture
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(autouse=True)
async def start_test_server(event_loop):
    await websockets.serve(start_server, TEST_SERVER_HOST, TEST_SERVER_PORT, loop=event_loop)


@pytest.fixture
def client_factory(event_loop):
    async def wrapped():
        return await websockets.connect(f'ws://{TEST_SERVER_HOST}:{TEST_SERVER_PORT}', loop=event_loop)
    return wrapped
