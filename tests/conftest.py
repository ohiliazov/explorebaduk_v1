import pytest


@pytest.fixture
def login_message():
    return {
        'action': 'login',
        'data': {
            'user_id': 'user_1',
            'token': 'token_1',
        }
    }
