from pydantic import BaseModel


class DomainEvent(BaseModel):
    """
    Domain events are used to communicate between aggregates within a single transaction boundary via in-memory queue.
    Domain events are synchronous in nature.
    """
