from contextvars import ContextVar
from sqlalchemy.sql.schema import Column
from sqlalchemy.orm import Session
from sqlalchemy_json import mutable_json_type
from sqlalchemy.dialects.postgresql import UUID, JSONB
from typing import Type
import uuid

from seedwork.domain.entities import Entity
from seedwork.infrastructure.database import Base

from modules.catalog.domain.repositories import ListingRepository
from modules.catalog.domain.entities import Listing

"""
References:
"Introduction to SQLAlchemy 2020 (Tutorial)" by: Mike Bayer
https://youtu.be/sO7FFPNvX2s?t=7214
"""


class CatalogListingModel(Base):
    __tablename__ = "catalog_listing"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data = Column(mutable_json_type(dbtype=JSONB, nested=True))


class JSONDataMapper:
    def data_to_entity(self, data: dict, entity_class: Type[Entity]) -> Entity:
        entity_id = uuid.UUID(data.pop("id"))
        entity_dict = {
            "id": entity_id,
            **data,
        }
        return entity_class(**entity_dict)

    def entity_to_data(self, entity: Entity, model_class):
        data = dict(**entity.__dict__)
        entity_id = str(data.pop("id"))
        return model_class(
            **{
                "id": entity_id,
                "data": data,
            }
        )


class PostgresJsonListingRepository(ListingRepository):
    """Listing repository implementation"""

    model = CatalogListingModel

    def __init__(self, db_session: ContextVar, mapper=JSONDataMapper()):
        self._session_cv = db_session
        self.mapper = mapper

    @property
    def session(self) -> Session:
        return self._session_cv.get()

    def get_by_id(self, listing_id: UUID) -> Listing:
        data = self.session.query(self.model).filter_by(id=str(listing_id)).one()
        entity = self.mapper.data_to_entity(data, Listing)
        return entity

    def insert(self, entity: Listing):
        data = self.mapper.entity_to_data(entity, self.model)
        self.session.add(data)

    def update(self, entity: Listing):
        raise NotImplementedError()

    def delete(self, entity: Listing):
        raise NotImplementedError()

    def count(self) -> int:
        return self.session.query(self.model).count()
