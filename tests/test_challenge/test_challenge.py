import pytest
from explorebaduk.message import parse_message
from explorebaduk.schema import NewChallengeSchema
from explorebaduk.constants import TimeSystem, Ruleset, GameType


@pytest.mark.parametrize(
    "message, expected",
    [
        (
            "challenge new GT0RL0PL2 19:19 F101 T1M3600O30P5S1B0D0 My Challenge",
            {
                "name": "My Challenge",
                "game_type": GameType.RANKED,
                "rules": Ruleset.JAPANESE,
                "players_num": 2,
                "width": 19,
                "height": 19,
                "is_open": True,
                "undo": False,
                "pause": True,
                "time_system": TimeSystem.ABSOLUTE,
                "main_time": 3600,
                "overtime": 0,
                "stones": 0,
                "periods": 0,
                "delay": 0,
                "bonus": 0,
            },
        )
    ],
)
def test_challenge(message, expected):
    message_type, parsed = parse_message(message)
    parsed.pop("action")
    result = NewChallengeSchema().load(parsed)
    assert result == expected
