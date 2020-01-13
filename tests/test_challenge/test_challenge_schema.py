import pytest

from explorebaduk.schema import ChallengeSchema
from explorebaduk.constants import TimeSystem


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            {
                "undo": "0",
                "pause": "0",
                "is_open": "0",
                "time_system": "0",
                "main_time": "3600",
                "overtime": "0",
                "periods": "0",
                "stones": "0",
                "bonus": "0",
                "delay": "0",
            },
            {
                "time_system": TimeSystem.NO_TIME,
                "is_open": False,
                "pause": False,
                "undo": False,
                "main_time": float("+inf"),
                "overtime": 0,
                "periods": 0,
                "stones": 0,
                "bonus": 0,
                "delay": 0,
            },
        ),
        (
            {
                "time_system": "1",
                "undo": "0",
                "pause": "1",
                "is_open": "0",
                "main_time": "3600",
                "overtime": "0",
                "periods": "0",
                "stones": "0",
                "bonus": "0",
                "delay": "0",
            },
            {
                "time_system": TimeSystem.ABSOLUTE,
                "is_open": False,
                "pause": True,
                "undo": False,
                "main_time": 3600,
                "overtime": 0,
                "periods": 0,
                "stones": 0,
                "bonus": 0,
                "delay": 0,
            },
        ),
        (
            {
                "time_system": "2",
                "undo": "1",
                "pause": "1",
                "is_open": "1",
                "main_time": "1800",
                "overtime": "30",
                "periods": "5",
                "stones": "9999",
                "bonus": "9999",
                "delay": "1",
            },
            {
                "time_system": TimeSystem.BYOYOMI,
                "is_open": True,
                "pause": True,
                "undo": True,
                "main_time": 1800,
                "overtime": 30,
                "periods": 5,
                "stones": 1,
                "bonus": 0,
                "delay": 1,
            },
        ),
        (
            {
                "time_system": "3",
                "undo": "1",
                "pause": "1",
                "is_open": "1",
                "main_time": "1800",
                "overtime": "300",
                "periods": "9999",
                "stones": "20",
                "bonus": "9999",
                "delay": "1",
            },
            {
                "time_system": TimeSystem.CANADIAN,
                "is_open": True,
                "pause": True,
                "undo": True,
                "main_time": 1800,
                "overtime": 300,
                "periods": 1,
                "stones": 20,
                "bonus": 0,
                "delay": 1,
            },
        ),
    ],
)
def test_challenge_schema(data, expected):
    result = ChallengeSchema().load(data)
    assert result == expected
