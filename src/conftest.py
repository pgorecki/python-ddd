import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from api.main import app as fastapi_instance
from config.api_config import ApiConfig
from modules.iam.application.services import IamService
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
def authenticated_api_client(api, app):
    access_token = uuid.uuid4()
    with app.transaction_context() as ctx:
        iam: IamService = ctx[IamService]
        current_user = iam.create_user(
            uuid.UUID(int=1),
            email="user1@example.com",
            password="password",
            access_token=str(access_token),
            is_superuser=False,
        )
    headers = {"Authorization": f"bearer {access_token}"}
    client = TestClient(api, headers=headers)
    client.current_user = current_user
    return client


@pytest.fixture
def app(api, db_session):
    app = api.container.application()
    return app
