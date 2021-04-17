import random

import pytest
from starlette.status import HTTP_200_OK


@pytest.mark.asyncio
async def test_get_friends(test_cli, db_friends):
    user = random.choice(db_friends).user
    test_cli.authorize(user)

    resp = await test_cli.get_friends()
    assert resp.status_code == HTTP_200_OK, resp.text

    expected = {
        "following": sorted(
            [f.friend_id for f in db_friends if f.user_id == user.user_id],
        ),
        "followers": sorted(
            [f.user_id for f in db_friends if f.friend_id == user.user_id],
        ),
    }
    assert resp.json() == expected


@pytest.mark.asyncio
async def test_get_user_friends(test_cli, db_friends):
    friendship = random.choice(db_friends)
    user = friendship.user
    friend_id = friendship.friend_id

    test_cli.authorize(user)

    resp = await test_cli.get_user_friends(friend_id)
    assert resp.status_code == HTTP_200_OK, resp.text

    expected = {
        "following": sorted(
            [f.friend_id for f in db_friends if f.user_id == friend_id],
        ),
        "followers": sorted(
            [f.user_id for f in db_friends if f.friend_id == friend_id],
        ),
    }
    assert resp.json() == expected
