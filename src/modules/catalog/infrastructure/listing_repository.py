from sqlalchemy.sql.schema import Column
from contextvars import ContextVar
from sqlalchemy.orm import Session
from sqlalchemy_json import mutable_json_type
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from seedwork.infrastructure.database import Base

from modules.catalog.domain.repositories import ListingRepository
from modules.catalog.domain.entities import Listing

"""
References:
"Introduction to SQLAlchemy 2020 (Tutorial)" by: Mike Bayer
https://youtu.be/sO7FFPNvX2s?t=7214
"""


class CatalogListing(Base):
    __tablename__ = "catalog_listing"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data = Column(mutable_json_type(dbtype=JSONB, nested=True))


class JsonMapper:
    ...


class PostgresJsonListingRepository(ListingRepository):
    """Listing repository implementation"""

    model = CatalogListing

    def __init__(self, db_session: ContextVar, mapper=JsonMapper()):
        self._session_cv = db_session
        self.mapper = mapper

    @property
    def session(self) -> Session:
        return self._session_cv.get()

    def get_by_id(self, id: UUID) -> Listing:
        model = self.session.query(CatalogListing).filter_by(id=str(id)).one()
        print(model)
        entity = self.mapper.model_to_entity(model)
        return entity

    def insert(self, entity: Listing):
        model = self.mapper.entity_to_model(entity)
        self.session.add(model)

    def update(self, entity: Listing):
        ...

    def delete(self, entity: Listing):
        ...

    def count(self) -> int:
        return self.session.query(self.model).count()
