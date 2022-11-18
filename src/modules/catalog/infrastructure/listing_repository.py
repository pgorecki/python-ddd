import uuid

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.schema import Column
from sqlalchemy_json import mutable_json_type
from sqlalchemy_utils import UUIDType

from modules.catalog.domain.entities import Listing, Money
from modules.catalog.domain.repositories import ListingRepository
from seedwork.infrastructure.database import Base
from seedwork.infrastructure.repository import SqlAlchemyGenericRepository

"""
References:
"Introduction to SQLAlchemy 2020 (Tutorial)" by: Mike Bayer
https://youtu.be/sO7FFPNvX2s?t=7214
"""


class ListingModel(Base):
    """Data model for listing domain object"""

    __tablename__ = "catalog_listing"
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    data = Column(mutable_json_type(dbtype=JSONB, nested=True))


class ListingDataMapper:
    def model_to_entity(self, instance: ListingModel) -> Listing:
        d = instance.data
        return Listing(
            id=instance.id,
            title=d["title"],
            description=d["description"],
            ask_price=Money(**d["ask_price"]),
            seller_id=uuid.UUID(d["seller_id"]),
        )

    def entity_to_model(self, entity: Listing) -> ListingModel:
        return ListingModel(
            id=entity.id,
            data={
                "title": entity.title,
                "description": entity.description,
                "ask_price": {
                    "amount": entity.ask_price.amount,
                    "currency": entity.ask_price.currency,
                },
                "seller_id": str(entity.seller_id),
                "status": entity.status,
            },
        )


class PostgresJsonListingRepository(SqlAlchemyGenericRepository, ListingRepository):
    """Listing repository implementation"""

    data_mapper = ListingDataMapper()
    model_class = ListingModel
