import os
import pytest

from explorebaduk.app import create_app


@pytest.yield_fixture()
def test_app():
    os.environ["CONFIG_PATH"] = "config/test.cfg"
    app = create_app()
    return app


@pytest.fixture
def test_cli(loop, test_app, test_client):
    return loop.run_until_complete(test_client(test_app))
