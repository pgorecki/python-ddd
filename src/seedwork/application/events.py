import sys
from dataclasses import dataclass, field
from typing import Any

from seedwork.domain.type_hints import DomainEvent
from seedwork.domain.value_objects import UUID


@dataclass
class EventResult:
    """
    Result of event execution (success or failure) by an event handler.
    """
    event_id: UUID = None
    payload: Any = None
    events: list[DomainEvent] = field(default_factory=list)
    errors: list[Any] = field(default_factory=list)

    def has_errors(self):
        """Returns True if an event execution failed"""
        return len(self.errors) > 0

    def is_success(self) -> bool:
        """Returns True if an event was successfully executed"""
        return not self.has_errors()
    
    def __hash__(self):
        return id(self)

    @classmethod
    def failure(cls, message="Failure", exception=None) -> "CommandResult":
        """Creates a failed result"""
        exception_info = sys.exc_info()
        errors = [(message, exception, exception_info)]
        result = cls(errors=errors)
        return result

    @classmethod
    def success(
        cls, event_id=None, payload=None, event=None, events=None
    ) -> "EventResult":
        """Creates a successful result"""
        if events is None:
            events = []
        if event:
            events.append(event)
        return cls(event_id=event_id, payload=payload, events=events)
    
    
class EventResultSet(set):
    """For now just aa fancy name for a set"""
    def is_success(self):
        return all([r.is_success() for r in self])
    
    @property
    def events(self):
        all_events = []
        for event in self:
            all_events.extend(event.events)
        return all_events