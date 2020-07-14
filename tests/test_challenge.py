async def test_post_challenge_only_required_fields(test_cli):
    payload = {
        "game_setup": {"name": "Test Name", "type": "ranked", "opponent_id": None},
        "rule_set": {"rules": "japanese", "board_size": 19, "handicap": None, "komi": None},
        "time_settings": {},
    }

    expected = {
        "game_setup": {"name": "Test Name", "type": "ranked", "is_private": False, "opponent_id": None},
        "rule_set": {"rules": "japanese", "board_size": 19, "handicap": None, "komi": None},
        "time_settings": {"main_time": 0, "overtime": 0, "periods": 1, "stones": 1, "bonus": 0},
    }

    resp = await test_cli.post("/challenges", json=payload)

    assert resp.status == 200

    resp_json = await resp.json()
    assert resp_json["challenge_data"] == expected


async def test_post_challenge_with_opponent(test_cli):
    payload = {
        "game_setup": {"name": "Test Name", "type": "ranked", "opponent_id": 1},
        "rule_set": {"rules": "japanese", "board_size": 19, "handicap": 2, "komi": 0.5},
        "time_settings": {},
    }

    expected = {
        "game_setup": {"name": "Test Name", "type": "ranked", "is_private": False, "opponent_id": 1},
        "rule_set": {"rules": "japanese", "board_size": 19, "handicap": 2, "komi": 0.5},
        "time_settings": {"main_time": 0, "overtime": 0, "periods": 1, "stones": 1, "bonus": 0},
    }

    resp = await test_cli.post("/challenges", json=payload)

    assert resp.status == 200

    resp_json = await resp.json()
    assert resp_json["challenge_data"] == expected
