from contextlib import ExitStack
from typing import List

import pytest
from fastapi import WebSocket
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from explorebaduk.database import BaseModel, SessionLocal
from explorebaduk.main import app
from explorebaduk.models import UserModel
from explorebaduk.utils.database import generate_users

engine = create_engine(
    "sqlite:///explorebaduk_test.sqlite3",
    connect_args={"check_same_thread": False},
)
SessionLocal.configure(bind=engine)


@pytest.fixture
def db_session() -> SessionLocal:
    session = SessionLocal()
    BaseModel.metadata.drop_all(session.bind)
    BaseModel.metadata.create_all(session.bind)
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_cli() -> TestClient:
    return TestClient(app)


@pytest.fixture
def ws(test_cli) -> WebSocket:
    with test_cli.websocket_connect("/ws") as websocket:
        yield websocket


@pytest.fixture
def websockets_guests(test_cli) -> List[WebSocket]:
    with ExitStack() as stack:
        contexts = [
            stack.enter_context(test_cli.websocket_connect("/ws")) for _ in range(10)
        ]
        print("here")
        yield contexts


@pytest.fixture
def db_users(db_session) -> List[UserModel]:
    return generate_users(db_session, 100)
