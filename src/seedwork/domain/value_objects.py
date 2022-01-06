import uuid
import functools
from pydantic.dataclasses import dataclass


UUID = uuid.UUID
UUID.v4 = uuid.uuid4


@dataclass
class ValueObject:
    """
    Base class for value objects
    """


@functools.total_ordering
@dataclass
class Money(ValueObject):
    amount: int = 0
    currency: str = "USD"

    def __eq__(self, other):
        assert self.currency == other.currency
        return self.amount == other.amount

    def __lt__(self, other):
        assert self.currency == other.currency
        return self.amount < other.amount

    def __repr__(self) -> str:
        return f"{self.amount}{self.currency}"
