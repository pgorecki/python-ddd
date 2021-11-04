from contextvars import ContextVar
from sqlalchemy.sql.schema import Column
from sqlalchemy.orm import Session
from sqlalchemy_json import mutable_json_type
from sqlalchemy.dialects.postgresql import UUID, JSONB
from typing import Type
import uuid

from seedwork.infrastructure.database import Base
from seedwork.infrastructure.json_data_mapper import JSONDataMapper

from modules.iam.domain.repositories import UserRepository
from modules.iam.domain.entities import User


class UserModel(Base):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data = Column(mutable_json_type(dbtype=JSONB, nested=True))


class PostgresJsonUserRepository(UserRepository):
    """User repository implementation"""

    model = UserModel

    def __init__(self, db_session: ContextVar, mapper=JSONDataMapper()):
        self._session_cv = db_session
        self.mapper = mapper

    @property
    def session(self) -> Session:
        return self._session_cv.get()

    def get_by_id(self, listing_id: UUID) -> User:
        data = self.session.query(self.model).filter_by(id=str(listing_id)).one()
        entity = self.mapper.data_to_entity(data, User)
        return entity

    def insert(self, entity: User):
        data = self.mapper.entity_to_data(entity, self.model)
        self.session.add(data)

    def update(self, entity: User):
        raise NotImplementedError()

    def delete(self, entity: User):
        raise NotImplementedError()

    def count(self) -> int:
        return self.session.query(self.model).count()
