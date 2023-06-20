import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from api.main import app as fastapi_instance
from config.api_config import ApiConfig
from seedwork.infrastructure.database import Base


@pytest.fixture
def engine():
    config = ApiConfig()
    eng = create_engine(config.DATABASE_URL, echo=config.DATABASE_ECHO)

    with eng.begin() as connection:
        Base.metadata.drop_all(connection)
        Base.metadata.create_all(connection)
        return eng


@pytest.fixture
def db_session(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture
def api():
    return fastapi_instance


@pytest.fixture
def api_client(api, app):
    client = TestClient(api)
    return client


@pytest.fixture
def app(api, db_session):
    app = api.container.application()
    return app
