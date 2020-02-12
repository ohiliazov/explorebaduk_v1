import pytest
from explorebaduk.message import parse_message
from explorebaduk.schema import NewChallengeSchema
from explorebaduk.constants import TimeSystem, Ruleset, GameType


@pytest.mark.parametrize(
    "message, expected",
    [
        (
                "challenge new GN[My Challenge]GI[0R0W19H19]FL[101]TS[1M3600]",
                {'bonus': 0,
                 'delay': 0,
                 'game_type': GameType.RANKED,
                 'height': 19,
                 'is_open': True,
                 'main_time': 3600,
                 'name': 'My Challenge',
                 'overtime': 0,
                 'pause': True,
                 'periods': 0,
                 'rank_lower': 0,
                 'rank_upper': 3000,
                 'rules': Ruleset.JAPANESE,
                 'stones': 0,
                 'time_system': TimeSystem.ABSOLUTE,
                 'undo': False,
                 'width': 19},
        )
    ],
)
def test_challenge(message, expected):
    message_type, parsed = parse_message(message)

    parsed.pop("action")
    result = NewChallengeSchema().load(parsed)
    assert result == expected
