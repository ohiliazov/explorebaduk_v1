import pytest

from explorebaduk.schema import TimeSystemSchema, FlagsSchema
from explorebaduk.constants import TimeSystem


@pytest.mark.parametrize(
    "data, expected",
    [
        ({"time_system": "0"}, {"time_system": TimeSystem.NO_TIME}),
        (
            {"time_system": "1", "main_time": "3600"},
            {"time_system": TimeSystem.ABSOLUTE, "main_time": 3600},
        ),
        (
            {"time_system": "2", "main_time": "1800", "overtime": "30", "periods": "5"},
            {
                "time_system": TimeSystem.BYOYOMI,
                "main_time": 1800,
                "overtime": 30,
                "periods": 5,
            },
        ),
        (
            {"time_system": "3", "main_time": "1800", "overtime": "300", "stones": "20",},
            {"time_system": TimeSystem.CANADIAN, "main_time": 1800, "overtime": 300, "stones": 20,},
        ),
    ],
)
def test_time_system_schema(data, expected):
    result = TimeSystemSchema().load(data)
    assert result == expected


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            {"is_open": "0", "undo": "0", "pause": "0"},
            {"is_open": False, "undo": False, "pause": False},
        ),
        (
            {"is_open": "1", "undo": "0", "pause": "0"},
            {"is_open": True, "undo": False, "pause": False},
        ),
        (
            {"is_open": "0", "undo": "1", "pause": "1"},
            {"is_open": False, "undo": True, "pause": True},
        ),
    ],
)
def test_flags_schema(data, expected):
    result = FlagsSchema().load(data)
    assert result == expected
