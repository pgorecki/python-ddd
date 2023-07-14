import sys
from dataclasses import dataclass, field
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")


@dataclass
class QueryResult(Generic[T]):
    payload: Optional[T] = None
    errors: list[Any] = field(default_factory=list)

    def has_errors(self):
        return len(self.errors) > 0

    def is_success(self) -> bool:
        return not self.has_errors()

    @classmethod
    def failure(cls, message="Failure", exception=None) -> "QueryResult":
        """Creates a failed result"""
        exception_info = sys.exc_info()
        errors = [(message, exception, exception_info)]
        result = cls(errors=errors)
        return result

    @classmethod
    def success(cls, payload=None) -> "QueryResult":
        """Creates a successful result"""
        return cls(payload=payload)
