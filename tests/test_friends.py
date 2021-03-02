import random

import pytest
from starlette.status import HTTP_200_OK

from explorebaduk.crud import get_friendships


@pytest.mark.asyncio
async def test_get_friends(test_cli, db_friends):
    user = random.choice(db_friends).user
    test_cli.authorize(user)

    resp = await test_cli.get_friends()
    assert resp.status_code == HTTP_200_OK, resp.text

    resp_json = resp.json()
    friends_in, friends_out = set(), set()
    for user_id, friend_id in get_friendships(user.user_id):
        if user_id != user.user_id:
            friends_in.add(user_id)
        elif friend_id != user.user_id:
            friends_out.add(friend_id)

    assert set(resp_json["friends"]) == friends_out & friends_in
    assert set(resp_json["friends_out"]) == friends_out - friends_in
    assert set(resp_json["friends_in"]) == friends_in - friends_out
