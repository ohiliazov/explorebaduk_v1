import pytest
from explorebaduk.message import parse_message
from explorebaduk.schema import NewChallengeSchema
from explorebaduk.constants import TimeSystem, Ruleset, GameType


@pytest.mark.parametrize(
    "message, expected",
    [
        (
            "challenge new GN[My Challenge]GI[0R0W19H19]FL[101]TS[1M3600]",
            {
                "name": "My Challenge",
                "game_type": GameType.RANKED,
                "rules": Ruleset.JAPANESE,
                "width": 19,
                "height": 19,
                "is_open": True,
                "undo": False,
                "pause": True,
                "time_system": TimeSystem.ABSOLUTE,
                "main_time": 3600,
            },
        )
    ],
)
def test_challenge(message, expected):
    message_type, parsed = parse_message(message)

    parsed.pop("action")
    result = NewChallengeSchema().load(parsed)
    assert result == expected
