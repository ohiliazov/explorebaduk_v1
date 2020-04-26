import asyncio
import functools
import websockets
import pytest

from config import get_config
from app import start_server

from explorebaduk.database import DatabaseHandler


config = get_config(env="test")
db_handler = DatabaseHandler(config["database_uri"])
server_uri = f"ws://{config['server_host']}:{config['server_port']}"


@pytest.fixture
def event_loop():
    return asyncio.get_event_loop()


@pytest.yield_fixture(autouse=True)
async def start_test_server(event_loop):
    server = await websockets.serve(
        ws_handler=functools.partial(start_server, db_handler=db_handler),
        host=config["server_host"],
        port=config["server_port"],
        loop=event_loop,
    )
    yield
    server.close()


@pytest.fixture
def ws_factory(event_loop):
    async def gen(i):
        return [
            await websockets.connect(server_uri, loop=event_loop) for _ in range(i)
        ]

    return gen


@pytest.yield_fixture
async def ws(event_loop):
    return await websockets.connect(server_uri, loop=event_loop)
