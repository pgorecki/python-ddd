import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from seedwork.infrastructure.database import Base

import api.config as config

engine = create_engine(config.DATABASE_URL, echo=config.DEBUG)


@pytest.fixture
def db_session():
    with engine.begin() as connection:
        Base.metadata.drop_all(connection)
        Base.metadata.create_all(connection)

    with Session(engine) as session:
        yield session
