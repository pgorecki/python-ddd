from pydantic import BaseModel


class Event(BaseModel):
    """Base class for domain events."""


class DomainEvent(Event):
    """
    Domain events are used to communicate between aggregates within a single transaction boundary via in-memory queue.
    Domain events are synchronous.
    """


class IntegrationEvent(Event):
    """
    Integration events are used to communicate between modules/system via inbox-outbox pattern.
    Integration events are asynchronous.
    """
