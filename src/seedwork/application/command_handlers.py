import sys
from dataclasses import dataclass, field
from typing import Any

from seedwork.domain.type_hints import DomainEvent
from seedwork.domain.value_objects import UUID


@dataclass
class CommandResult:
    entity_id: UUID = None
    payload: Any = None
    events: list[DomainEvent] = field(default_factory=list)
    errors: list[Any] = field(default_factory=list)

    def has_errors(self):
        return len(self.errors) > 0

    def is_success(self) -> bool:
        return not self.has_errors()

    @classmethod
    def failure(cls, message="Failure", exception=None) -> "CommandResult":
        """Creates a failed result"""
        exception_info = sys.exc_info()
        errors = [(message, exception, exception_info)]
        result = cls(errors=errors)
        return result

    @classmethod
    def success(cls, entity_id=None, payload=None, events=[]) -> "CommandResult":
        """Creates a successful result"""
        return cls(entity_id=entity_id, payload=payload, events=events)


class CommandHandler:
    """
    Base class for command handlers
    """
