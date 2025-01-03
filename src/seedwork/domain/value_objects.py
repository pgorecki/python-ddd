import uuid
from dataclasses import dataclass
from typing import Any

from pydantic import GetCoreSchemaHandler


class GenericUUID(uuid.UUID):
    @classmethod
    def next_id(cls):
        return cls(int=uuid.uuid4().int)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ):
        return handler.generate_schema(uuid.UUID)


class ValueObject:
    """
    Base class for value objects
    """


# @functools.total_ordering  # type: ignore
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
        return Money(self.amount + other.amount, currency=self.currency)

    def __repr__(self) -> str:
        return f"{self.amount}{self.currency}"


class Email(str):
    def __new__(cls, email):
        if "@" not in email:
            raise ValueError("Invalid email address")
        return super().__new__(cls, email)
