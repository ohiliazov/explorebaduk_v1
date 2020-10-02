import random

from tests.conftest import receive_messages


async def test_challenges_connect(test_cli, users_data: list):
    user_data = random.choice(users_data)
    ws = await test_cli.ws_connect(
        test_cli.app.url_for("Challenges Feed"),
        headers={"Authorization": user_data["token"].token},
    )

    assert not await receive_messages(ws)
