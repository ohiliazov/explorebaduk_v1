import random

import pytest
from starlette.status import HTTP_200_OK


@pytest.mark.asyncio
async def test_get_players(test_cli, db_users):
    resp = await test_cli.get_players()
    assert resp.status_code == HTTP_200_OK, resp.text

    assert resp.json() == [user.asdict() for user in db_users]


@pytest.mark.asyncio
@pytest.mark.parametrize("attr", ["first_name", "last_name", "full_name"])
async def test_get_players_search_last_name(test_cli, db_users, attr):
    q = getattr(random.choice(db_users), attr)
    resp = await test_cli.get_players(q)
    assert resp.status_code == HTTP_200_OK, resp.text

    expected = [user.asdict() for user in db_users if q in getattr(user, attr)]
    assert resp.json() == expected
