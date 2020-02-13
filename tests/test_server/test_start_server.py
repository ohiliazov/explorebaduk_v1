import pytest
import random

from explorebaduk.database import UserModel, TokenModel

CONNECTED_CLIENTS = 10


def get_user(db, user_id):
    user = db.query(UserModel).filter_by(user_id=user_id).first()
    return user


def random_token(db):
    user = random.choice(list(db.query(TokenModel).all()))
    return user


@pytest.mark.asyncio
async def test_auth_login(db_session, client_factory):
    token = random_token(db_session)
    user = get_user(db_session, token.user_id)
    print(token.token)
    print(user.full_name)
    ws1 = await client_factory()
    await ws1.send(f"auth login {token.token}")
    print(await ws1.recv())
    print(await ws1.recv())
    print(await ws1.recv())
