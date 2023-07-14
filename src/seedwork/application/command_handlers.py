import sys
from dataclasses import dataclass, field
from typing import Any, Optional

from seedwork.domain.type_hints import DomainEvent
from seedwork.domain.value_objects import GenericUUID


@dataclass
class CommandResult:
    entity_id: Optional[GenericUUID] = None
    payload: Any = None
    events: list[DomainEvent] = field(default_factory=list)
    errors: list[Any] = field(default_factory=list)

    def has_errors(self):
        return len(self.errors) > 0

    def add_error(self, message, exception, exception_info):
        self.errors.append((message, exception, exception_info))

    def is_success(self) -> bool:
        return not self.has_errors()

    @classmethod
    def failure(cls, message="Failure", exception=None) -> "CommandResult":
        """Creates a failed result"""
        exception_info = sys.exc_info()
        result = cls()
        result.add_error(message, exception, exception_info)
        return result

    @classmethod
    def success(
        cls, entity_id=None, payload=None, event=None, events=None
    ) -> "CommandResult":
        """Creates a successful result"""
        if events is None:
            events = []
        if event:
            events.append(event)
        return cls(entity_id=entity_id, payload=payload, events=events)
