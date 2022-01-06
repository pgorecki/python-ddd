from datetime import datetime
from pydantic.dataclasses import dataclass, Field
from seedwork.domain.value_objects import ValueObject, Money, UUID


@dataclass
class Bidder(ValueObject):
    uuid: UUID


@dataclass
class Seller(ValueObject):
    uuid: UUID


@dataclass
class Bid(ValueObject):
    price: Money
    bidder: Bidder
    placed_at: datetime = Field(default_factory=datetime.utcnow)
