from pydantic import BaseModel, Field

from seedwork.domain.value_objects import GenericUUID


class DomainEvent(BaseModel):
    """
    Domain events are used to communicate between aggregates within a single transaction boundary via in-memory queue.
    Domain events are synchronous in nature.
    """

    event_id: GenericUUID = Field(default_factory=GenericUUID)
    # correlation_id: GenericUUID
    # causation_id: GenericUUID

    def __next__(self):
        yield self


class CompositeDomainEvent(DomainEvent):
    events: list[DomainEvent]

    def __next__(self):
        yield from self.events
