import sys
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field

from seedwork.domain.type_hints import DomainEvent
from seedwork.domain.value_objects import GenericUUID


class EventId(GenericUUID):
    """Unique identifier of an event"""


class IntegrationEvent(BaseModel):
    """
    Integration events are used to communicate between modules/system via inbox-outbox pattern.
    They are created in a domain event handler and then saved in an outbox for further delivery.
    As a result, integration events are handled asynchronously.
    """

    event_id: GenericUUID = Field(default_factory=GenericUUID)


@dataclass
class EventResult:
    """
    Result of event execution (success or failure) by an event handler.
    """

    event_id: EventId = field(default_factory=EventId.next_id)
    payload: Any = None
    events: list[DomainEvent] = field(default_factory=list)  # triggered events
    errors: list[Any] = field(default_factory=list)

    def has_errors(self) -> bool:
        """Returns True if an event execution failed"""
        return len(self.errors) > 0

    def is_success(self) -> bool:
        """Returns True if an event was successfully executed"""
        return not self.has_errors()

    def extend_with_events(self, events: list[DomainEvent]):
        self.events.extend(events)

    def __hash__(self):
        return id(self)

    @classmethod
    def failure(cls, message="Failure", exception=None) -> "EventResult":
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
