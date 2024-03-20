import datetime
import uuid

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.schema import Column
from sqlalchemy_json import mutable_json_type
from sqlalchemy_utils import UUIDType

from modules.bidding.domain.entities import Bid, Bidder, Listing, Money, Seller
from modules.bidding.domain.repositories import ListingRepository
from seedwork.domain.value_objects import GenericUUID
from seedwork.infrastructure.database import Base
from seedwork.infrastructure.repository import SqlAlchemyGenericRepository

"""
References:
"Introduction to SQLAlchemy 2020 (Tutorial)" by: Mike Bayer
https://youtu.be/sO7FFPNvX2s?t=7214
"""


class ListingModel(Base):
    """Data model for listing domain object in the bidding context"""

    __tablename__ = "bidding_listing"
    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    data = Column(mutable_json_type(dbtype=JSONB, nested=True))


def serialize_money(money: Money) -> dict:
    return {
        "amount": money.amount,
        "currency": money.currency,
    }


def serialize_id(value: GenericUUID) -> str:
    return str(value)


def deserialize_id(value: str) -> GenericUUID:
    if isinstance(value, uuid.UUID):
        return GenericUUID(value.hex)
    return GenericUUID(value)


def deserialize_money(data: dict) -> Money:
    return Money(data["amount"], currency=data["currency"])


def serialize_datetime(value: datetime.datetime) -> str:
    return value.isoformat()


def deserialize_datetime(value: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(value)


def serialize_bid(bid: Bid) -> dict:
    return {
        "bidder_id": serialize_id(bid.bidder.id),
        "max_price": serialize_money(bid.max_price),
        "placed_at": serialize_datetime(bid.placed_at),
    }


def deserialize_bid(data: dict) -> Bid:
    return Bid(
        bidder=Bidder(id=deserialize_id(data["bidder_id"])),
        max_price=deserialize_money(data["max_price"]),
        placed_at=deserialize_datetime(data["placed_at"]),
    )


class ListingDataMapper:
    def model_to_entity(self, instance: ListingModel) -> Listing:
        d = instance.data
        return Listing(
            id=deserialize_id(instance.id),
            seller=Seller(id=deserialize_id(d["seller_id"])),
            ask_price=deserialize_money(d["ask_price"]),
            starts_at=deserialize_datetime(d["starts_at"]),
            ends_at=deserialize_datetime(d["ends_at"]),
        )

    def entity_to_model(self, entity: Listing) -> ListingModel:
        return ListingModel(
            id=entity.id,
            data={
                "starts_at": serialize_datetime(entity.starts_at),
                "ends_at": serialize_datetime(entity.ends_at),
                "ask_price": serialize_money(entity.ask_price),
                "seller_id": serialize_id(entity.seller.id),
                "bids": [serialize_bid(b) for b in entity.bids],
            },
        )


class PostgresJsonListingRepository(SqlAlchemyGenericRepository, ListingRepository):
    """Listing repository implementation"""

    mapper_class = ListingDataMapper
    model_class = ListingModel
