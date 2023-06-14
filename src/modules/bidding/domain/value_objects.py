from datetime import datetime

from pydantic.dataclasses import Field, dataclass

from seedwork.domain.value_objects import UUID, Money, ValueObject


@dataclass(frozen=True)
class Bidder(ValueObject):
    id: UUID


@dataclass(frozen=True)
class Seller(ValueObject):
    id: UUID


@dataclass(frozen=True)
class Bid(ValueObject):
    max_price: Money  # a maximum price that a bidder is willing to pay
    bidder: Bidder
    placed_at: datetime = Field(default_factory=datetime.utcnow)
