from cerberus.validator import Validator

from explorebaduk.constants import (
    ALLOWED_GAME_TYPES,
    ALLOWED_RULES,
    ALLOWED_TIME_SYSTEMS,
    ALLOWED_HANDICAP_STONES,
)


def is_valid_komi(field, value: float, error):
    if value is not None and not float(value * 2).is_integer():
        error(field, "Invalid komi")


challenge_schema = {
    "game_setup": {
        "type": "dict",
        "require_all": True,
        "schema": {
            "name": {"type": "string", "empty": False},
            "type": {"type": "string", "allowed": ALLOWED_GAME_TYPES},
            "is_private": {"type": "boolean", "default": False},
        },
    },
    "rule_set": {
        "type": "dict",
        "require_all": True,
        "schema": {
            "rules": {"type": "string", "allowed": ALLOWED_RULES},
            "board_size": {"type": "integer", "default": 19, "min": 5, "max": 52},
        },
    },
    "time_settings": {
        "type": "dict",
        "schema": {
            "time_system": {"type": "string", "allowed": ALLOWED_TIME_SYSTEMS},
            "main_time": {"type": "integer", "default": 0, "min": 0},
            "overtime": {"type": "integer", "default": 0, "min": 0},
            "periods": {"type": "integer", "default": 1, "min": 1},
            "stones": {"type": "integer", "default": 1, "min": 1},
            "bonus": {"type": "integer", "default": 0, "min": 0},
        },
    },
}

join_schema = {
    "handicap": {
        "type": "integer",
        "nullable": True,
        "allowed": ALLOWED_HANDICAP_STONES,
    },
    "komi": {"type": "float", "nullable": True, "check_with": is_valid_komi},
}

challenge_validator = Validator(challenge_schema, allow_unknown=False)
join_validator = Validator(join_schema, allow_unknown=False)
