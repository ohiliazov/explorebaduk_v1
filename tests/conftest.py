import os
import pytest
import random
import string
import datetime

from sanic.websocket import WebSocketProtocol

from explorebaduk.app import create_app
from explorebaduk.database import BaseModel, UserModel, TokenModel


@pytest.yield_fixture()
def test_app():
    os.environ["CONFIG_PATH"] = "config/test.cfg"
    app = create_app()

    return app


@pytest.fixture
def test_cli(loop, test_app, test_client):
    return loop.run_until_complete(test_client(test_app, protocol=WebSocketProtocol))


@pytest.fixture
async def users_data(test_app):
    db = test_app.db
    BaseModel.metadata.drop_all(db.engine)
    BaseModel.metadata.create_all(db.engine)

    users_data = []

    for user_id in range(1, 101):
        token = f"{string.ascii_letters}{user_id:012d}"

        user_data = {
            "user_id": user_id,
            "first_name": "John",
            "last_name": f"Doe#{user_id}",
            "email": f"johndoe{user_id}@explorebaduk.com",
            "rating": random.randint(0, 3000),
            "puzzle_rating": random.randint(0, 3000),
        }
        token_data = {
            "token_id": user_id,
            "user_id": user_id,
            "token": token,
            "expired_at": datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
        }
        db.save(UserModel(**user_data))
        db.save(TokenModel(**token_data))
        users_data.append((user_id, token))

    return users_data
