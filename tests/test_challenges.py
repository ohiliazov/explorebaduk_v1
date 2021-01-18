import random

from explorebaduk.constants import EventName, RouteName
from explorebaduk.utils.test_utils import (
    generate_challenge_data,
    generate_expected_challenge_data,
    receive_all,
    receive_messages,
)


async def test_challenges_create(test_cli, challenges_online: dict, challenge_owners_online: dict):
    owner_ws, owner_data = random.choice(list(challenge_owners_online.items()))

    challenge_data = generate_challenge_data()

    resp = await test_cli.post(
        test_cli.app.url_for(RouteName.CHALLENGES_VIEW),
        json=challenge_data,
        headers={"Authorization": owner_data["token"].token},
    )

    expected_challenge = generate_expected_challenge_data(owner_data["user"].user_id, challenge_data)

    assert resp.status == 201
    assert await resp.json() == expected_challenge

    expected = {"event": EventName.CHALLENGE_SET, "data": {"message": "Challenge set"}}
    assert expected in await receive_messages(owner_ws)

    expected = {
        "event": EventName.CHALLENGES_ADD,
        "data": expected_challenge,
    }
    for ws_messages in await receive_all(challenges_online):
        assert expected in ws_messages


async def test_delete_challenge(test_cli, users_data: list, challenges_online: dict, challenge_owners_online: dict):
    owner_ws, owner_data = random.choice(list(challenge_owners_online.items()))
    challenge_data = generate_challenge_data()

    await owner_ws.send_json({"event": EventName.CHALLENGE_SET, "data": challenge_data})
    await receive_messages(owner_ws)
    await receive_all(challenges_online)

    owner_id = owner_data["user"].user_id
    response = await test_cli.delete(
        test_cli.app.url_for(RouteName.CHALLENGES_VIEW, challenge_id=owner_id),
        headers={"Authorization": owner_data["token"].token},
    )

    assert response.status == 200
    assert await response.json() == {"message": "Challenge unset"}

    expected = {
        "event": EventName.CHALLENGE_UNSET,
        "data": {"message": "Challenge unset"},
    }
    assert expected in await receive_messages(owner_ws)

    expected = {
        "event": EventName.CHALLENGES_REMOVE,
        "data": {"user_id": owner_id},
    }
    for ws_messages in await receive_all(challenges_online):
        assert expected in ws_messages


async def test_set_challenge(test_cli, challenges_online: dict, challenge_owners_online: dict):
    ws, user_data = random.choice(list(challenge_owners_online.items()))
    challenge_data = generate_challenge_data()

    await ws.send_json({"event": EventName.CHALLENGE_SET, "data": challenge_data})

    event_message = {
        "event": EventName.CHALLENGE_SET,
        "data": {"message": "Challenge set"},
    }
    assert event_message in await receive_messages(ws)

    expected = {
        "event": EventName.CHALLENGES_ADD,
        "data": generate_expected_challenge_data(user_data["user"].user_id, challenge_data),
    }
    for ws_messages in await receive_all(challenges_online):
        assert expected in ws_messages


async def test_unset_challenge(test_cli, challenges_online: dict, challenge_owners_online: dict):
    ws, user_data = random.choice(list(challenge_owners_online.items()))
    challenge_data = generate_challenge_data()

    await ws.send_json({"event": EventName.CHALLENGE_SET, "data": challenge_data})
    await receive_all(challenge_owners_online)
    await receive_all(challenges_online)
    await ws.send_json({"event": EventName.CHALLENGE_UNSET})

    expected = {
        "event": EventName.CHALLENGE_UNSET,
        "data": {"message": "Challenge unset"},
    }
    assert expected in await receive_messages(ws)

    expected = {
        "event": EventName.CHALLENGES_REMOVE,
        "data": {"user_id": user_data["user"].user_id},
    }
    for ws_messages in await receive_all(challenges_online):
        assert expected in ws_messages


async def test_set_challenge_update(test_cli, challenges_online: dict, challenge_owners_online: dict):
    ws, user_data = random.choice(list(challenge_owners_online.items()))
    challenge_data = generate_challenge_data()

    await ws.send_json({"event": EventName.CHALLENGE_SET, "data": challenge_data})
    await receive_all(challenge_owners_online)
    await receive_all(challenges_online)

    challenge_data = generate_challenge_data()
    await ws.send_json({"event": EventName.CHALLENGE_SET, "data": challenge_data})

    ws_messages = await receive_messages(ws)
    expected_unset_ok = {
        "event": EventName.CHALLENGE_UNSET,
        "data": {"message": "Challenge unset"},
    }
    expected_set_ok = {
        "event": EventName.CHALLENGE_SET,
        "data": {"message": "Challenge set"},
    }
    assert expected_unset_ok in ws_messages
    assert expected_set_ok in ws_messages

    expected_challenges_remove = {
        "event": EventName.CHALLENGES_REMOVE,
        "data": {"user_id": user_data["user"].user_id},
    }
    expected_challenges_add = {
        "event": EventName.CHALLENGES_ADD,
        "data": generate_expected_challenge_data(user_data["user"].user_id, challenge_data),
    }
    for ws_messages in await receive_all(challenges_online):
        assert expected_challenges_remove in ws_messages
        assert expected_challenges_add in ws_messages


async def test_unset_challenge_disconnect(test_cli, challenges_online: dict, challenge_owners_online: dict):
    ws, user_data = random.choice(list(challenge_owners_online.items()))
    challenge_data = generate_challenge_data()

    await ws.send_json({"event": EventName.CHALLENGE_SET, "data": challenge_data})
    await receive_all(challenge_owners_online)
    await receive_all(challenges_online)

    await ws.close()

    expected = {
        "event": EventName.CHALLENGES_REMOVE,
        "data": {"user_id": user_data["user"].user_id},
    }
    for ws_messages in await receive_all(challenges_online):
        assert expected in ws_messages


async def test_unset_challenge_not_set(test_cli, challenges_online: dict, challenge_owners_online: dict):
    ws, user_data = random.choice(list(challenge_owners_online.items()))

    await ws.send_json({"event": EventName.CHALLENGE_UNSET})
    expected = {
        "event": "error",
        "data": {"message": "Challenge not set"},
    }
    assert expected in await receive_messages(ws)


async def test_join_challenge(test_cli, users_data: list, challenges_online: dict, challenge_owners_online: dict):
    owner_ws, owner_data = random.choice(list(challenge_owners_online.items()))
    challenge_data = generate_challenge_data()

    await owner_ws.send_json({"event": EventName.CHALLENGE_SET, "data": challenge_data})
    await receive_messages(owner_ws)
    await receive_all(challenges_online)

    owner_id = owner_data["user"].user_id
    ws = await test_cli.ws_connect(test_cli.app.url_for("Challenge Feed", challenge_id=owner_id))

    user_data = random.choice([user_data for user_data in users_data if user_data != owner_data])
    await ws.send_json({"event": EventName.AUTHORIZE, "data": {"token": user_data["token"].token}})
    await ws.send_json({"event": EventName.CHALLENGE_JOIN})

    expected = {
        "event": EventName.CHALLENGE_JOIN,
        "data": user_data["user"].as_dict(),
    }
    assert expected in await receive_messages(owner_ws)

    expected = {
        "event": EventName.CHALLENGE_JOIN,
        "data": {"message": "Joined"},
    }
    assert expected in await receive_messages(ws)


async def test_leave_challenge(test_cli, users_data: list, challenges_online: dict, challenge_owners_online: dict):
    owner_ws, owner_data = random.choice(list(challenge_owners_online.items()))
    challenge_data = generate_challenge_data()

    await owner_ws.send_json({"event": EventName.CHALLENGE_SET, "data": challenge_data})
    await receive_messages(owner_ws)
    await receive_all(challenges_online)

    owner_id = owner_data["user"].user_id
    ws = await test_cli.ws_connect(test_cli.app.url_for("Challenge Feed", challenge_id=owner_id))

    user_data = random.choice([user_data for user_data in users_data if user_data != owner_data])
    await ws.send_json({"event": EventName.AUTHORIZE, "data": {"token": user_data["token"].token}})
    await ws.send_json({"event": EventName.CHALLENGE_JOIN})
    await receive_all({owner_ws, ws})

    await ws.send_json({"event": EventName.CHALLENGE_LEAVE})

    expected = {
        "event": EventName.CHALLENGE_LEAVE,
        "data": {"user_id": user_data["user"].user_id},
    }
    assert expected in await receive_messages(owner_ws)

    expected = {
        "event": EventName.CHALLENGE_LEAVE,
        "data": {"message": "Left"},
    }
    assert expected in await receive_messages(ws)
