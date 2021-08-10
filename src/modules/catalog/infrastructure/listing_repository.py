from sqlalchemy import Table
from sqlalchemy.sql.schema import Column
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.sqltypes import String, Integer, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID

from seedwork.infrastructure.database import Base

from modules.catalog.domain.value_objects import ListingStatus
from modules.catalog.domain.repositories import ListingRepository
from modules.catalog.domain.entities import Listing

"""
References:
"Introduction to SQLAlchemy 2020 (Tutorial)" by: Mike Bayer
https://youtu.be/sO7FFPNvX2s?t=7214
"""

from sqlalchemy.orm import declarative_base


class ListingModel(Base):
    __tablename__ = "catalog_listing"
    id = Column(UUID(as_uuid=True), primary_key=True)
    id = Column(String, primary_key=True)
    title = Column(String(128))
    description = Column(Text)
    price = Column(Numeric)
    seller_id = Column(UUID(as_uuid=True))
    status = Column(String)


class ListingMapper:
    """Maps attributes betweer Listing and ListingModel"""

    def model_to_entity(self, model: ListingModel) -> Listing:
        data = model.__dict__
        return Listing(**data)

    def entity_to_model(self, entity: Listing) -> ListingModel:
        data = entity.dict()
        return ListingModel(**data)


class SqlListingRepository(ListingRepository):
    """Listing repository implementation"""

    def __init__(self, db_session: Session, mapper=ListingMapper()) -> None:
        self.session = db_session
        self.mapper = mapper

    def get_by_id(self, id: UUID) -> Listing:
        model = self.session.query(ListingModel).filter_by(id=str(id)).one()
        entity = self.mapper.model_to_entity(model)
        return entity

    def insert(self, entity: Listing):
        model = self.mapper.entity_to_model(entity)
        self.session.add(model)

    def count(self) -> int:
        return self.session.query(ListingModel).count()
