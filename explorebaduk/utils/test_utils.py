import asyncio
import random

from explorebaduk.constants import (
    ALLOWED_GAME_TYPES,
    ALLOWED_RULES,
    ALLOWED_TIME_SYSTEMS,
)


async def receive_messages(ws, sort_by: callable = None, timeout: float = 0.5):
    messages = []
    try:
        while True:
            messages.append(await ws.receive_json(timeout=timeout))
    except asyncio.TimeoutError:
        pass

    if sort_by:
        messages = sorted(messages, key=sort_by)

    return messages


async def receive_all(ws_list, sort_by: callable = None, timeout: float = 0.5):
    return await asyncio.gather(*[receive_messages(ws, sort_by, timeout) for ws in ws_list])


def generate_time_settings(time_system: str, **kwargs):
    time_settings = {
        "time_system": time_system,
        **kwargs,
    }

    if time_system == "unlimited":
        return time_settings

    time_settings.setdefault("main_time", random.randint(1, 3600))
    if time_system == "absolute":
        return time_settings

    if time_system == "fischer":
        time_settings.setdefault("bonus", random.randint(1, 10))
        return time_settings

    time_settings.setdefault("overtime", random.randint(1, 60))
    if time_system == "byoyomi":
        time_settings.setdefault("stones", 1)
    elif time_system == "canadian":
        time_settings.setdefault("periods", 1)

    return time_settings


def generate_challenge_data(game_type: str = None, rules: str = None, time_system: str = None, **kwargs):
    game_type = game_type or random.choice(ALLOWED_GAME_TYPES)
    rules = rules or random.choice(ALLOWED_RULES)
    time_system = time_system or random.choice(ALLOWED_TIME_SYSTEMS)
    time_settings = generate_time_settings(time_system, **kwargs)

    return {
        "game_setup": {
            "name": f"Game {random.randint(1, 99999)}",
            "type": game_type,
        },
        "rule_set": {
            "rules": rules,
        },
        "time_settings": time_settings,
    }


def generate_expected_challenge_data(user_id, expected: dict):
    return {
        "user_id": user_id,
        "game_setup": {
            "is_private": False,
            **expected["game_setup"],
        },
        "rule_set": {
            "board_size": 19,
            **expected["rule_set"],
        },
        "time_settings": {
            "main_time": 0,
            "overtime": 0,
            "periods": 1,
            "stones": 1,
            "bonus": 0,
            **expected["time_settings"],
        },
    }
