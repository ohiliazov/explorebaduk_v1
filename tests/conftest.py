import os
from contextlib import ExitStack
from typing import List

import pytest
from sqlalchemy import create_engine
from starlette.testclient import TestClient, WebSocketTestSession

from explorebaduk.database import BaseModel, SessionLocal
from explorebaduk.main import app

from .helpers import receive_messages

BASE_DIR = os.path.dirname(__file__)
TEST_DATABASE_PATH = os.path.join(BASE_DIR, os.path.pardir, "explorebaduk_test.sqlite3")
TEST_DATABASE_URI = f"sqlite:///{os.path.abspath(TEST_DATABASE_PATH)}"
engine = create_engine(TEST_DATABASE_URI)
SessionLocal.configure(bind=engine)


@pytest.fixture
def db_session():
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def test_cli() -> TestClient:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def db_users(db_session):
    pass


@pytest.fixture
def websocket(test_cli) -> WebSocketTestSession:
    with test_cli.websocket_connect("/ws") as websocket:
        yield websocket


@pytest.fixture
async def guest_websockets(test_cli) -> List[WebSocketTestSession]:
    with ExitStack() as stack:
        websockets = []
        for _ in range(2):
            websocket = stack.enter_context(test_cli.websocket_connect("/ws"))
            websockets.append(websocket)

            websocket.send_json({"event": "authorize", "data": None})
            print(receive_messages(websocket))

        yield websockets
