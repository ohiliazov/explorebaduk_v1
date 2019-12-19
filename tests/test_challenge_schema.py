import pytest
from explorebaduk.schema import ChallengeSchema


@pytest.fixture
def rule_set():
    return {'rules': 'japanese',
            'board_height': 19,
            'to_join': 1}


@pytest.fixture
def no_restrictions():
    return {'no_undo': False,
            'no_pause': False,
            'no_analyze': False,
            'is_private': False}


@pytest.fixture
def time_absolute():
    return {'type': 'absolute',
            'main': 3600}


@pytest.fixture
def time_byoyomi():
    return {'type': 'byoyomi',
            'main': 3600,
            'overtime': 30,
            'periods': 3}


@pytest.fixture
def time_canadian():
    return {'type': 'canadian',
            'main': 3600,
            'overtime': 600,
            'stones': 25}


@pytest.fixture
def time_fischer():
    return {'type': 'fischer',
            'main': 3600,
            'bonus': 10}


@pytest.fixture
def time_no_time():
    return {'type': 'no_time'}


def test_challenge_schema(rule_set, time_absolute, no_restrictions):
    data = {
        'type': 'ranked',
        'name': 'My Challenge Name',
        'rule_set': rule_set,
        'time_system': time_absolute,
        'restrictions': no_restrictions,
    }
    print(data)
    result = ChallengeSchema().load(data)

    expected = {
        'type': 'ranked',
        'name': 'My Challenge Name',
        'rule_set': {**rule_set,
                     'board_width': 19},
        'time_system': {**time_absolute,
                        'overtime': 0,
                        'periods': 0,
                        'stones': 0,
                        'bonus': 0,
                        'delay': 0},
        'restrictions': no_restrictions,
    }
    assert result == expected
