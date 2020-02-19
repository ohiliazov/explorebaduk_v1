import pytest

from explorebaduk.message import parse_message


@pytest.mark.parametrize(
    "message, expected",
    [
        [
            "challenge new GN[My Challenge]GI[0R0W19H19]FL[000]TS[0M3600O0P0S0B0D0]",
            {
                "action": "new",
                "game_type": "0",
                "name": "My Challenge",
                "rules": "0",
                "width": "19",
                "height": "19",
                "is_open": "0",
                "undo": "0",
                "pause": "0",
                "time_system": "0",
                "main_time": "3600",
                "overtime": "0",
                "periods": "0",
                "stones": "0",
                "bonus": "0",
                "delay": "0",
            },
        ],
    ],
)
def test_message_challenge(message, expected):
    message_type, data = parse_message(message)
    assert data == expected
