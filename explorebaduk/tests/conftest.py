import pytest
import os
from sqlalchemy import create_engine
from explorebaduk.config import TEST_DATABASE_PATH, TEST_DATABASE_URI
from explorebaduk.database import create_session, BaseModel


@pytest.fixture(scope='session')
def engine():
    return create_engine(TEST_DATABASE_URI)


@pytest.yield_fixture(scope='session')
def db(engine):
    BaseModel.metadata.create_all(engine)
    yield
    BaseModel.metadata.drop_all(engine)
