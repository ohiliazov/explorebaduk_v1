import random

import pytest
from starlette.status import HTTP_200_OK


@pytest.mark.asyncio
async def test_get_followers(test_cli, db_friends):
    user = random.choice(db_friends).user
    test_cli.authorize(user)

    resp = await test_cli.get_followers()
    assert resp.status_code == HTTP_200_OK, resp.text

    expected = [f for f in db_friends if f.friend_id == user.user_id]
    assert len(resp.json()) == len(expected)


@pytest.mark.asyncio
async def test_get_following(test_cli, db_friends):
    user = random.choice(db_friends).user
    test_cli.authorize(user)

    resp = await test_cli.get_following()
    assert resp.status_code == HTTP_200_OK, resp.text

    expected = [f for f in db_friends if f.user_id == user.user_id]
    assert len(resp.json()) == len(expected)
