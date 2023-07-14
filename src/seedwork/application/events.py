import sys
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel

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


@dataclass
class EventResult:
    """
    Result of event execution (success or failure) by an event handler.
    """

    event_id: EventId = field(default_factory=EventId.next_id)
    payload: Any = None
    command: Any = (
        None  # command to be executed as a result of this event (experimental)
    )
    events: list[DomainEvent] = field(default_factory=list)
    errors: list[Any] = field(default_factory=list)

    def has_errors(self) -> bool:
        """Returns True if an event execution failed"""
        return len(self.errors) > 0

    def is_success(self) -> bool:
        """Returns True if an event was successfully executed"""
        return not self.has_errors()

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
        cls, event_id=None, payload=None, command=None, event=None, events=None
    ) -> "EventResult":
        """Creates a successful result"""
        if events is None:
            events = []
        if event:
            events.append(event)
        return cls(event_id=event_id, payload=payload, command=command, events=events)


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

    @property
    def commands(self):
        all_commands = [event.command for event in self if event.command]
        return all_commands
