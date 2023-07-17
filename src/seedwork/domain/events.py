from pydantic import BaseModel


class DomainEvent(BaseModel):
    """
    Domain events are used to communicate between aggregates within a single transaction boundary via in-memory queue.
    Domain events are synchronous in nature.
    """

    def __next__(self):
        yield self


class CompositeDomainEvent(DomainEvent):
    events: list[DomainEvent]

    def __next__(self):
        yield from self.events
