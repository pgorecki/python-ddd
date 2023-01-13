import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from api.main import app
from config.api_config import ApiConfig
from seedwork.infrastructure.database import Base


@pytest.fixture
def engine():
    config = ApiConfig()
    engine = create_engine(config.DATABASE_URL, echo=config.DEBUG)

    with engine.begin() as connection:
        Base.metadata.drop_all(connection)
        Base.metadata.create_all(connection)
        print("---- engine ready ----")
        return engine


@pytest.fixture
def db_session(engine):

    with Session(engine) as session:
        yield session


@pytest.fixture
def api(engine):
    return app


@pytest.fixture
def api_client(api):
    client = TestClient(api)
    return client
