import random

from explorebaduk.utils.test_utils import (
    generate_challenge_data,
    generate_expected_challenge_data,
)
from tests.conftest import receive_all, receive_messages


async def test_challenges_create(test_cli, challenges_online: dict):
    user_data = random.choice(list(challenges_online.values()))
    challenge_data = generate_challenge_data()

    resp = await test_cli.post(
        test_cli.app.url_for("Challenges View"),
        json=challenge_data,
        headers={"Authorization": user_data["token"].token},
    )

    assert resp.status == 201

    expected = {
        "event": "challenges.add",
        "data": generate_expected_challenge_data(user_data["user"].user_id, challenge_data),
    }
    for ws_messages in await receive_all(challenges_online):
        assert expected in ws_messages


async def test_challenges_update(test_cli, challenges_online: dict):
    user_data = random.choice(list(challenges_online.values()))
    challenge_data = generate_challenge_data()

    await test_cli.post(
        test_cli.app.url_for("Challenges View"),
        json=challenge_data,
        headers={"Authorization": user_data["token"].token},
    )
    await receive_all(challenges_online)

    challenge_data = generate_challenge_data()
    resp = await test_cli.post(
        test_cli.app.url_for("Challenges View"),
        json=challenge_data,
        headers={"Authorization": user_data["token"].token},
    )
    assert resp.status == 201

    expected = {
        "event": "challenges.update",
        "data": generate_expected_challenge_data(user_data["user"].user_id, challenge_data),
    }
    for ws_messages in await receive_all(challenges_online):
        assert expected in ws_messages


async def test_set_challenge(test_cli, challenges_online: dict, challenge_owners_online: dict):
    ws, user_data = random.choice(list(challenge_owners_online.items()))
    challenge_data = generate_challenge_data()

    await ws.send_json({"event": "challenge.set", "data": challenge_data})

    event_message = {
        "event": "set.ok",
        "data": {"message": "Challenge set"},
    }
    assert event_message in await receive_messages(ws)

    expected = {
        "event": "challenges.add",
        "data": generate_expected_challenge_data(user_data["user"].user_id, challenge_data),
    }
    for ws_messages in await receive_all(challenges_online):
        assert expected in ws_messages


async def test_unset_challenge(test_cli, challenges_online: dict, challenge_owners_online: dict):
    ws, user_data = random.choice(list(challenge_owners_online.items()))
    challenge_data = generate_challenge_data()

    await ws.send_json({"event": "challenge.set", "data": challenge_data})
    await receive_all(challenge_owners_online)
    await receive_all(challenges_online)
    await ws.send_json({"event": "challenge.unset"})

    expected = {
        "event": "unset.ok",
        "data": {"message": "Challenge unset"},
    }
    assert expected in await receive_messages(ws)

    expected = {
        "event": "challenges.remove",
        "data": {"user_id": user_data["user"].user_id},
    }
    for ws_messages in await receive_all(challenges_online):
        assert expected in ws_messages


async def test_set_challenge_update(test_cli, challenges_online: dict, challenge_owners_online: dict):
    ws, user_data = random.choice(list(challenge_owners_online.items()))
    challenge_data = generate_challenge_data()

    await ws.send_json({"event": "challenge.set", "data": challenge_data})
    await receive_all(challenge_owners_online)
    await receive_all(challenges_online)

    challenge_data = generate_challenge_data()
    await ws.send_json({"event": "challenge.set", "data": challenge_data})

    ws_messages = await receive_messages(ws)
    expected_unset_ok = {
        "event": "unset.ok",
        "data": {"message": "Challenge unset"},
    }
    expected_set_ok = {
        "event": "set.ok",
        "data": {"message": "Challenge set"},
    }
    assert expected_unset_ok in ws_messages
    assert expected_set_ok in ws_messages

    expected_challenges_remove = {
        "event": "challenges.remove",
        "data": {"user_id": user_data["user"].user_id},
    }
    expected_challenges_add = {
        "event": "challenges.add",
        "data": generate_expected_challenge_data(user_data["user"].user_id, challenge_data),
    }
    for ws_messages in await receive_all(challenges_online):
        assert expected_challenges_remove in ws_messages
        assert expected_challenges_add in ws_messages


async def test_unset_challenge_disconnect(test_cli, challenges_online: dict, challenge_owners_online: dict):
    ws, user_data = random.choice(list(challenge_owners_online.items()))
    challenge_data = generate_challenge_data()

    await ws.send_json({"event": "challenge.set", "data": challenge_data})
    await receive_all(challenge_owners_online)
    await receive_all(challenges_online)

    await ws.close()

    expected = {
        "event": "challenges.remove",
        "data": {"user_id": user_data["user"].user_id},
    }
    for ws_messages in await receive_all(challenges_online):
        assert expected in ws_messages


async def test_unset_challenge_not_set(test_cli, challenges_online: dict, challenge_owners_online: dict):
    ws, user_data = random.choice(list(challenge_owners_online.items()))

    await ws.send_json({"event": "challenge.unset"})
    expected = {
        "event": "unset.error",
        "data": {"message": "Challenge not set"},
    }
    assert expected in await receive_messages(ws)


async def test_join_challenge(test_cli, users_data: list, challenges_online: dict, challenge_owners_online: dict):
    owner_ws, owner_data = random.choice(list(challenge_owners_online.items()))
    challenge_data = generate_challenge_data()

    await owner_ws.send_json({"event": "challenge.set", "data": challenge_data})
    await receive_messages(owner_ws)
    await receive_all(challenges_online)

    owner_id = owner_data["user"].user_id
    ws = await test_cli.ws_connect(test_cli.app.url_for("Challenge Owner Feed", challenge_id=owner_id))

    user_data = random.choice([user_data for user_data in users_data if user_data != owner_data])
    await ws.send_json({"event": "authorize", "data": {"token": user_data["token"].token}})
    print(await receive_messages(ws))
    await ws.send_json({"event": "challenge.join"})

    expected = {
        "event": "challenge.join",
        "data": user_data["user"].as_dict(),
    }
    assert expected in await receive_messages(owner_ws)

    expected = {
        "event": "join.ok",
        "data": {"message": "Joined"},
    }
    assert expected in await receive_messages(ws)
