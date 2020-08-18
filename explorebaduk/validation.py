from cerberus.validator import Validator


def is_valid_komi(field, value: float, error):
    if value is not None and not float(value * 2).is_integer():
        error(field, "Invalid komi")


challenge_schema = {
    "game_setup": {
        "type": "dict",
        "require_all": True,
        "schema": {
            "name": {"type": "string", "empty": False},
            "type": {"type": "string", "allowed": ["ranked", "free"]},
            "is_private": {"type": "boolean", "default": False},
            "opponent_id": {"type": "integer", "nullable": True},
        },
    },
    "rule_set": {
        "type": "dict",
        "require_all": True,
        "schema": {
            "rules": {"type": "string", "allowed": ["japanese", "chinese"]},
            "board_size": {"type": "integer", "min": 5, "max": 52},
            "handicap": {"type": "integer", "nullable": True, "allowed": [0, 2, 3, 4, 5, 6, 7, 8, 9]},
            "komi": {"type": "float", "nullable": True, "check_with": is_valid_komi},
        },
    },
    "time_settings": {
        "type": "dict",
        "schema": {
            "time_system": {"type": "string", "allowed": ["unlimited", "absolute", "byo-yomi", "canadian", "fischer"]},
            "main_time": {"type": "integer", "default": 0, "min": 0},
            "overtime": {"type": "integer", "default": 0, "min": 0},
            "periods": {"type": "integer", "default": 1, "min": 1},
            "stones": {"type": "integer", "default": 1, "min": 1},
            "bonus": {"type": "integer", "default": 0, "min": 0},
        },
    },
}

challenge_validator = Validator(challenge_schema, allow_unknown=False)
