import functools
import uuid

from pydantic.dataclasses import dataclass

UUID = uuid.UUID
UUID.v4 = uuid.uuid4


@dataclass(frozen=True)
class ValueObject:
    """
    Base class for value objects
    """


@functools.total_ordering
@dataclass(frozen=True)
class Money(ValueObject):
    amount: int = 0
    currency: str = "USD"

    def _check_currency(self, other):
        if self.currency != other.currency:
            raise ValueError("Cannot compare money of different currencies")

    def __eq__(self, other):
        self._check_currency(other)
        return self.amount == other.amount

    def __lt__(self, other):
        self._check_currency(other)
        return self.amount < other.amount

    def __add__(self, other):
        self._check_currency(other)
        return Money(amount=self.amount + other.amount, currency=self.currency)

    def __repr__(self) -> str:
        return f"{self.amount}{self.currency}"


class Email(str):
    def __new__(cls, email):
        if "@" not in email:
            raise ValueError("Invalid email address")
        return super().__new__(cls, email)
