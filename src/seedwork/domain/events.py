from pydantic import BaseModel


class Event(BaseModel):
    pass


class DomainEvent(Event):
    pass


class IntegrationEvent(Event):
    pass
