from datetime import datetime

from pydantic.dataclasses import Field, dataclass

from seedwork.domain.value_objects import UUID, Money, ValueObject


@dataclass
class Bidder(ValueObject):
    id: UUID


@dataclass
class Seller(ValueObject):
    id: UUID


@dataclass
class Bid(ValueObject):
    price: Money
    bidder: Bidder
    placed_at: datetime = Field(default_factory=datetime.utcnow)
