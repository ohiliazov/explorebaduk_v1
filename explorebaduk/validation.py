from cerberus.validator import Validator

from explorebaduk.constants import (
    ALLOWED_GAME_TYPES,
    ALLOWED_HANDICAP_STONES,
    ALLOWED_RULES,
    ALLOWED_TIME_SYSTEMS,
)


def is_valid_komi(field, value: float, error):
    if value is not None and not float(value * 2).is_integer():
        error(field, "Invalid komi")


create_game_schema = {
    "game_setup": {
        "type": "dict",
        "required": True,
        "require_all": True,
        "schema": {
            "name": {"type": "string", "empty": False},
            "type": {"type": "string", "allowed": ALLOWED_GAME_TYPES},
            "is_private": {"type": "boolean", "default": False},
        },
    },
    "rule_set": {
        "type": "dict",
        "required": True,
        "require_all": True,
        "schema": {
            "rules": {"type": "string", "allowed": ALLOWED_RULES},
            "board_size": {"type": "integer", "default": 19, "min": 5, "max": 52},
        },
    },
    "time_settings": {
        "type": "dict",
        "required": True,
        "require_all": True,
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

join_game_schema = {
    "handicap": {
        "type": "integer",
        "nullable": True,
        "allowed": ALLOWED_HANDICAP_STONES,
    },
    "komi": {"type": "float", "nullable": True, "check_with": is_valid_komi},
}


def validate_payload(data, schema):
    """Validates payload and returns normalized data and errors"""
    validator = Validator(schema, allow_unknown=False)
    validator.validate(data)
    return validator.normalized(data), validator.errors
